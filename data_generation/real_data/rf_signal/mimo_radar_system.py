import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from data_generation.real_data.rf_signal.data_manipulation import data_manipulation_module
from data_generation.real_data.rf_signal.radar_module import RadarModule
from data_generation.real_data.rf_signal.switch_module import SwitchModule
from itertools import chain
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from data_generation.real_data.rf_signal.signal_convert import _convert_correlation, _convert_wiener_deconv
import datetime
import csv, os


class MimoRadarSystem:
    def __init__(self, num_tx_antenna: int, num_rx_antenna: int, radar_info: Dict, switch_info: Dict,
                 is_mimo: bool = True, h_t_mode: str = None, snr_for_wiener_dB: float = 1):
        self._radar = None
        self.set_up_radar(radar_info)
        self._num_sample = self._radar.num_sample
        self._tx_switch = None
        self._rx_switch = None
        self._is_mimo = is_mimo
        self.set_up_switch(switch_info)
        if self._is_mimo:
            self._num_tx_antenna = num_tx_antenna
            self._num_rx_antenna = num_rx_antenna
        else:
            self._num_tx_antenna = 1
            self._num_rx_antenna = 1
        self._radar_pulse = None
        self._radar_pulse_stretched = None
        self._radar_pulse_stretched_f = None
        self._radar_offset_stretched = None
        self._time_smoothing_coefficient = None
        self._time_smoothed_radar_signal = None
        self._clutter_update_coefficient = None
        self._clutter_signal = None
        self._is_attenuation_compensated = False
        self._attenuation_compensation_coefficient = None
        self._h_t_mode = h_t_mode
        self._h_t_is_abs = None
        self._h_t_lpf_f_cut_off_frequency = None
        self._h_t_lpf_t_cut_off_frequency = None

        self._data_mani_module = data_manipulation_module()

        self._snr_for_wiener_dB = snr_for_wiener_dB
        self.cnt = 0
        self._nowDate = None

        self.raw_signal = None

        matplotlib.use('TkAgg')

    def set_up_radar(self, radar_info: Dict):
        self._radar = RadarModule(radar_info['radar_lib_path'])
        if radar_info['band'] == 'low':
            self._radar.set_to_low_band()
        else:
            self._radar.set_to_medium_band()
        self._radar.set_timing_variables(radar_info['sample_delay_to_reference'],
                                         radar_info['offset_distance_from_reference'], radar_info['frame_stitch'])
        self._radar.set_gain(radar_info['gain'])
        # self._radar.set_averaging_factor(radar_info['averaging_factor'])
        # self._radar.set_iterations(radar_info['iterations'])
        self._radar.set_zoom(radar_info['zoom_min'], radar_info['zoom_max'])

    def set_up_switch(self, switch_info: Dict):
        if self._is_mimo:
            self._tx_switch = SwitchModule(switch_info['switch_lib_path'], switch_info['tx_switch_serial_number'])
            self._rx_switch = SwitchModule(switch_info['switch_lib_path'], switch_info['rx_switch_serial_number'])

    def set_tx_switch_port(self, idx_antenna: int):
        if self._is_mimo:
            self._tx_switch.set_switch_port(idx_antenna + 1)

    def set_rx_switch_port(self, idx_antenna: int):
        if self._is_mimo:
            self._rx_switch.set_switch_port(idx_antenna + 1)

    def set_time_absolute(self):
        self._h_t_is_abs = True

    def set_low_pass_filter_alg_f(self, cut_off_freq):
        self._h_t_lpf_f_cut_off_frequency = cut_off_freq
        self._h_t_lpf_t_cut_off_frequency = None

    def set_low_pass_filter_alg_t(self, cut_off_freq):
        self._h_t_lpf_f_cut_off_frequency = None
        self._h_t_lpf_t_cut_off_frequency = cut_off_freq

    def set_time_smoothing_filter(self, time_smoothing_coefficient: float):
        self._time_smoothing_coefficient = time_smoothing_coefficient
        self._time_smoothed_radar_signal = np.zeros((self._num_tx_antenna, self._num_rx_antenna, self._num_sample))

    def set_clutter_filter(self, clutter_update_coefficient: float):
        self._clutter_update_coefficient = clutter_update_coefficient
        self._clutter_signal = np.zeros((self._num_tx_antenna, self._num_rx_antenna, self._num_sample))

    #   펄스 파일이 들어있는 폴더의 주소를 입력한다.
    #   file name should be
    #   'tx port'_'rx port'_'samples per second'.csv
    #   ex) 01_02_36010101010.csv
    def set_offset_signal_dir(self, pulse_dir):
        file_list = os.listdir(pulse_dir)

        max_tx = 1
        max_rx = 1

        entire_file_list = []
        temp_file_list = []

        entire_sps_list = []
        temp_sps_list = []

        for file_name in file_list:
            temp_name = file_name.split('.')[0].split('_')
            port_tx = int(temp_name[0])
            port_rx = int(temp_name[1])
            sps = int(temp_name[2])

            if max_tx < port_tx:
                max_tx = port_tx
                entire_file_list.append(temp_file_list)
                entire_sps_list.append(temp_sps_list)
                temp_file_list = []
                temp_sps_list = []
            temp_file_list.append(pulse_dir + file_name)
            temp_sps_list.append(sps)
        entire_file_list.append(temp_file_list)
        entire_sps_list.append(temp_sps_list)
        entire_file_list = np.array(entire_file_list)
        entire_sps_list = np.array(entire_sps_list)

        self.set_entire_offset_signal(entire_file_list, entire_sps_list)

    def set_entire_offset_signal(self, pulse_file_name_list, sps_list=None):

        len_row = len(pulse_file_name_list)
        if len_row != self._num_tx_antenna:
            print("row size is wrong, it should be %d which are same as size of tx antenna", self._num_tx_antenna)
            return None

        len_col = len(pulse_file_name_list[0])
        if len_col != self._num_rx_antenna:
            print("col size is wrong, it should be %d which are same as size of rx antenna", self._num_rx_antenna)
            return None

        frame_stitch = int(self._radar.get_frame_stitch())
        sample_spacing = self._radar.get_sample_spacing()

        self._radar_offset_stretched = np.zeros([self._num_tx_antenna, self._num_rx_antenna, 512 * frame_stitch], dtype=complex)

        for i in range(len_row):
            for j in range(len_col):
                with open(str(Path(pulse_file_name_list[i][j]).resolve())) as f:
                    reader = csv.reader(f)
                    radar_pulse = np.array([list(map(float, row)) for row in reader])

                    if radar_pulse[0].size > 1:
                        radar_pulse_x = radar_pulse[:, 0]
                        radar_pulse_y = radar_pulse[:, 1]
                    else:
                        if sps_list is None:
                            sps = 3.6e+10
                            spacing = 10 ** 9 / sps
                        else:
                            sps = sps_list[i][j]
                            spacing = 10 ** 9 / sps
                        radar_pulse_x = np.arange(radar_pulse.size) * spacing
                        radar_pulse_y = radar_pulse[:, 0]

                    x = np.arange(radar_pulse_x[0], radar_pulse_x[-1], sample_spacing)
                    interp_radar_pulse = np.interp(x, radar_pulse_x, radar_pulse_y)
                    centered_radar_pulse = np.subtract(interp_radar_pulse, np.mean(interp_radar_pulse))
                    normalized_radar_pulse = np.divide(centered_radar_pulse, np.linalg.norm(centered_radar_pulse))

                    for k in range(len(normalized_radar_pulse)):
                        if k == len(self._radar_offset_stretched[i][j]):
                            break
                        self._radar_offset_stretched[i][j][k] = interp_radar_pulse[k]


        return self._radar_offset_stretched

    #   펄스 파일이 들어있는 폴더의 주소를 입력한다.
    #   file name should be
    #   'short or long'_'tx port'_'rx port'_'samples per second'.csv
    def set_entire_matched_filter_input_dir(self, pulse_dir):
        file_list = os.listdir(pulse_dir)
        max_tx = 1
        max_rx = 1

        entire_file_list = []
        temp_file_list = []

        entire_sps_list = []
        temp_sps_list = []

        for file_name in file_list:
            temp_name = file_name.split('.')
            temp_name = temp_name[0].split('_')
            port_tx = int(temp_name[0])
            port_rx = int(temp_name[1])
            sps = int(temp_name[2])

            if max_tx < port_tx:
                max_tx = port_tx
                entire_file_list.append(temp_file_list)
                entire_sps_list.append(temp_sps_list)
                temp_file_list = []
                temp_sps_list = []
            temp_file_list.append(pulse_dir + file_name)
            temp_sps_list.append(sps)
        entire_file_list.append(temp_file_list)
        entire_sps_list.append(temp_sps_list)
        entire_file_list = np.array(entire_file_list)
        entire_sps_list = np.array(entire_sps_list)

        self.set_entire_matched_filter(entire_file_list, entire_sps_list)

    #   펄스 파일 이름의 리스트를 넣어준다.
    #   Samples per seconds 의 리스트도 넣어준다.
    def set_entire_matched_filter(self, pulse_file_name_list, sps_list=None):

        len_row = len(pulse_file_name_list)
        if len_row != self._num_tx_antenna:
            print("row size is wrong, num of tx antenna is %d but row size of list is %d" %(self._num_tx_antenna, len_row))

        len_col = len(pulse_file_name_list[0])
        if len_col != self._num_rx_antenna:
            print("col size is wrong, num of rx antenna is %d but col size of list is %d" %(self._num_rx_antenna, len_col))

        len_row = self._num_tx_antenna
        len_col = self._num_rx_antenna

        frame_stitch = int(self._radar.get_frame_stitch())
        sample_spacing = self._radar.get_sample_spacing()
        chip_sps = self._radar.get_samples_per_second()
        print("Now sample spacing is ", chip_sps, " samples per second is %d" % chip_sps)

        self._radar_pulse = []  #   We are not sure about length of interpolated radar pulse
        self._radar_pulse_stretched = np.zeros([self._num_tx_antenna, self._num_rx_antenna, 512 * frame_stitch], dtype=complex)
        self._radar_pulse_stretched_f = np.zeros([self._num_tx_antenna, self._num_rx_antenna, 512 * frame_stitch], dtype=complex)

        for i in range(len_row):
            temp_pulse = []
            for j in range(len_col):
                with open(str(Path(pulse_file_name_list[i][j]).resolve())) as f:
                    reader = csv.reader(f)
                    radar_pulse = np.array([list(map(float, row)) for row in reader])

                    if radar_pulse[0].size > 1:
                        radar_pulse_x = radar_pulse[:, 0]
                        radar_pulse_y = radar_pulse[:, 1]
                    else:
                        if sps_list is None:
                            sps = 3.6e+10
                            spacing = 10 ** 9 / sps
                        else:
                            sps = sps_list[i][j]
                            spacing = 10 ** 9 / sps
                        radar_pulse_x = np.arange(radar_pulse.size) * spacing
                        radar_pulse_y = radar_pulse[:, 0]

                    x = np.arange(radar_pulse_x[0], radar_pulse_x[-1], sample_spacing)
                    interp_radar_pulse = np.interp(x, radar_pulse_x, radar_pulse_y)
                    centered_radar_pulse = np.subtract(interp_radar_pulse, np.mean(interp_radar_pulse))
                    normalized_radar_pulse = np.divide(centered_radar_pulse, np.linalg.norm(centered_radar_pulse))

                    temp_pulse.append(normalized_radar_pulse)

                    for k in range(len(normalized_radar_pulse)):
                        if k == len(self._radar_pulse_stretched[i][j]):
                            break
                        self._radar_pulse_stretched[i][j][k] = normalized_radar_pulse[k]

                    self._radar_pulse_stretched_f[i][j] = np.fft.fft(self._radar_pulse_stretched[i][j])
                    self._radar_pulse_stretched_f[i][j][0] = 1
            self._radar_pulse.append(temp_pulse)
        self._radar_pulse = np.array(self._radar_pulse)
        return self._radar_pulse

    def set_matched_filter(self, radar_pulse_file: str):
        with open(str(Path(radar_pulse_file).resolve()), 'r', newline='') as f:
            reader = csv.reader(f)
            radar_pulse = np.array([list(map(float, row)) for row in reader])

        sps = 3.6e+10
        spacing = 10 ** 9 / sps

        if radar_pulse[0].size > 1:
            radar_pulse_x = radar_pulse[:, 0]
            radar_pulse_y = radar_pulse[:, 1]
        else:
            radar_pulse_x = np.arange(radar_pulse.size) * spacing
            radar_pulse_y = radar_pulse[:, 0]

        sample_spacing = self._radar.get_sample_spacing()

        x = np.arange(radar_pulse_x[0], radar_pulse_x[-1], sample_spacing)

        interp_radar_pulse = np.interp(x, radar_pulse_x, radar_pulse_y)
        centered_radar_pulse = interp_radar_pulse - np.mean(interp_radar_pulse)
        normalized_radar_pulse = centered_radar_pulse / np.linalg.norm(centered_radar_pulse)

        self._radar_pulse = normalized_radar_pulse

        self._radar_pulse_stretched = np.zeros(self._radar.get_samplers_per_frame())
        for i in range(len(self._radar_pulse)):
            if i == len(self._radar_pulse_stretched):
                break
            self._radar_pulse_stretched[i] = self._radar_pulse[i]
        self._radar_pulse_stretched_f = np.fft.fft(self._radar_pulse_stretched)
        self._radar_pulse_stretched_f[0] = 1

    def set_attenuation_compensation_filter(self):
        self._is_attenuation_compensated = True
        self._attenuation_compensation_coefficient = self._radar.get_sample_distance() * 2

    def get_sample_time(self):
        return self._radar.get_sample_time()

    # 모든 송수신 안테나에 대해서 신호를 수신 및 처리
    def get_radar_signal(self, idx_tx=None, idx_rx=None):
        radar_signal = self._radar.get_frame_normalized_double()
        self.raw_signal = self._radar.get_frame_normalized_double()
        #   프레임별로 수신값이 DC 변동이 생길 수 있다.
        for i in range(4):
            radar_signal[i * 512:i * 512 + 512] = radar_signal[i * 512:i * 512 + 512] - np.mean(
                radar_signal[i * 512:i * 512 + 512])

        if self._radar_offset_stretched is not None:
            radar_signal = radar_signal - self._radar_offset_stretched[idx_tx][idx_rx]

        if self._radar_pulse is not None:
            if self._h_t_mode[:4] == 'corr':
                radar_signal = _convert_correlation(self._radar_pulse_stretched[idx_tx][idx_rx], radar_signal, \
                                                    mode='same')
            elif self._h_t_mode[:6] == 'wiener':
                radar_signal = _convert_wiener_deconv(self._radar_pulse_stretched[idx_tx][idx_rx], radar_signal,
                                                      snr_dB=self._snr_for_wiener_dB)
            elif self._h_t_mode[:6] == 'deconv':
                radar_signal = self._data_mani_module.convert_deconvolution(self._radar_pulse_stretched[idx_tx][idx_rx], radar_signal)

            elif self._h_t_mode[:4] == 'none':
                radar_signal = radar_signal

            if self._h_t_is_abs:
                radar_signal = np.abs(radar_signal)

            if self._h_t_lpf_f_cut_off_frequency:
                radar_signal = self._data_mani_module.convert_filter_lpf_f(radar_signal,self._h_t_lpf_f_cut_off_frequency)
            # elif self._h_t_lpf_t_cut_off_frequency

        return radar_signal

    def get_radar_signal_test(self):
        radar_signal = self._radar.get_frame_normalized_double()
        for i in range(4):
            radar_signal[i * 512:i * 512 + 512] = radar_signal[i * 512:i * 512 + 512] - np.mean(
                radar_signal[i * 512:i * 512 + 512])
        return radar_signal, self._radar_pulse, np.correlate(radar_signal, self._radar_pulse, 'same')

    def get_all_radar_signal(self):
        # print("now %d frame" % (self.cnt))
        self.cnt = self.cnt + 1

        radar_signal = np.zeros((self._num_tx_antenna, self._num_rx_antenna, self._num_sample), dtype=complex)

        for tx_ant in range(self._num_tx_antenna):
            self.set_tx_switch_port(tx_ant)
            for rx_ant in range(self._num_rx_antenna):
                self.set_rx_switch_port(rx_ant)
                radar_signal[tx_ant, rx_ant, :] = self.get_radar_signal(tx_ant, rx_ant)

        if self._clutter_update_coefficient is not None:
            coef = self._clutter_update_coefficient
            self._clutter_signal = coef * radar_signal + (1 - coef) * self._clutter_signal
        if self._time_smoothing_coefficient is not None:
            coef = self._time_smoothing_coefficient
            self._time_smoothed_radar_signal = coef * radar_signal + (1 - coef) * self._time_smoothed_radar_signal
            radar_signal = self._time_smoothed_radar_signal
        if self._clutter_update_coefficient is not None:
            radar_signal = radar_signal - self._clutter_signal
        if self._is_attenuation_compensated:
            radar_signal = radar_signal * self._attenuation_compensation_coefficient[np.newaxis, np.newaxis, :]
        return radar_signal

    def save_radar_signal2(self):
        while True:
            radar_signal = self.get_all_radar_signal()
            print(radar_signal.shape)
            print(radar_signal[0][0][:])

    @staticmethod
    def save_radar_signal(x_data: np.ndarray, radar_signal: np.ndarray, file_name: str):
        merged_signal = np.transpose(np.concatenate((x_data[np.newaxis, :], radar_signal.reshape((-1, x_data.size))),
                                                    axis=0))
        with open(str(Path(file_name).resolve()), 'w', newline='') as f:
            writer = csv.writer(f)
            for signal in merged_signal:
                writer.writerow(list(map(str, signal.real)))


    def _animate_radar_signal(self, frame, *fargs):
        (x_data, lines, capture_interval) = fargs

        radar_signal = self.get_all_radar_signal()

        for tx_ant in range(self._num_tx_antenna):
            for rx_ant in range(self._num_rx_antenna):
                line = lines[tx_ant][rx_ant]
                line.set_xdata(x_data)
                line.set_ydata(radar_signal[tx_ant, rx_ant])
        if (capture_interval is not None) and (frame > 0) and ((frame % capture_interval) == 0):
            self._nowDate = datetime.datetime.now()
            file_name = '____RADAR/%s_%s.csv' % (str(frame/5).zfill(8), self._nowDate.strftime("%S"))
            self.save_radar_signal(x_data, radar_signal, file_name=file_name)
        return chain.from_iterable(lines)

    def draw_radar_signal(self, num_frame: int = 1, x_axis: str = 'distance', y_axis_min_max: Tuple = (0, 100),
                          fig_size: Tuple = (4.5, 3.5), capture_interval: Optional[int] = None):
        plt.ion()
        fig, axes = plt.subplots(self._num_tx_antenna, self._num_rx_antenna,
                                 figsize=(fig_size[0] * self._num_rx_antenna, fig_size[1] * self._num_tx_antenna))
        if self._num_tx_antenna == 1:
            axes = np.expand_dims(axes, axis=0)
        if self._num_rx_antenna == 1:
            axes = np.expand_dims(axes, axis=1)

        if x_axis == 'time':
            x_data = self.get_sample_time()
            x_label = 'Time (ns)'
        elif x_axis == 'distance':
            x_data = self._radar.get_sample_distance()
            x_label = 'Distance (meter)'
        else:
            x_data = np.array([row for row in range(self._radar.get_samplers_per_frame())])
            x_label = 'Sample (sample)'

        if self._radar_pulse_stretched is not None:
            y_axis_min_max = np.array([y_axis_min_max[0], y_axis_min_max[1]], dtype=float)
            y_axis_min_max[0] = y_axis_min_max[0]*0.1
            y_axis_min_max[1] = y_axis_min_max[1]*0.1
        lines = []

        for tx_axes in axes:
            tx_lines = []

            for ax in tx_axes:
                ax.set_xlim(x_data[0], x_data[-1])
                ax.set_ylim(y_axis_min_max[0], y_axis_min_max[1])
                ax.set_xlabel(x_label)
                tx_lines.append(ax.plot([], [])[0])

            lines.append(tx_lines)

        fig.show()
        animation.FuncAnimation(fig, self._animate_radar_signal, frames=num_frame,
                                fargs=(x_data, lines, capture_interval), interval=0, blit=True)

    def measure_single_pulse(self, port_tx, port_rx, distance_m: float=1.0,averaging_factor: int = 1, is_print :bool=False):

        c = 299792458

        self._tx_switch.set_switch_port(port_tx)
        self._rx_switch.set_switch_port(port_rx)
        print("Measuring Pulse signal...")

        sum_radar_signal = 0

        for j in range(averaging_factor):
            radar_signal = self._radar.get_frame_normalized_double()
            for i in range(4):
                radar_signal[i * 512:i * 512 + 512] = radar_signal[i * 512:i * 512 + 512] - np.mean(
                    radar_signal[i * 512:i * 512 + 512])
            sum_radar_signal = radar_signal + sum_radar_signal
        sum_radar_signal = np.divide(sum_radar_signal, averaging_factor)
        radar_signal = sum_radar_signal

        sps = int(round(self._radar.get_samples_per_second(), 0))

        file_name = 'pulses_short/%02d_%02d_%d.csv' % (port_tx, port_rx, sps)

        length_short = 384
        length_middle = 768
        length_long = 1024

        pulse_start_idx = int(round(distance_m * sps / c))

        temp_max = np.max(radar_signal)

        if temp_max < 5:
            print("신호가 너무 약한것 같습니다. 확인하여 저장할지 여부를 결정하고, 본 조건문을 설정해주십시오. ")
            exit(1)

        print("Measuring (%d, %d)'s short pulse..." % (port_tx, port_rx))
        with open(str(Path(file_name).resolve()), 'w', newline='') as f:
            writer = csv.writer(f)
            for signal in radar_signal[pulse_start_idx:pulse_start_idx + length_short]:
                writer.writerow([signal])
        print("Short index is %d" % pulse_start_idx)

        print("Measuring (%d, %d)'s middle pulse..." % (port_tx, port_rx))
        file_name = 'pulses_middle/%02d_%02d_%d.csv' % (port_tx, port_rx, sps)
        with open(str(Path(file_name).resolve()), 'w', newline='') as f:
            writer = csv.writer(f)
            for signal in radar_signal[pulse_start_idx:pulse_start_idx + length_middle]:
                writer.writerow([signal])
        print("middle index is %d" % pulse_start_idx)

        print("Measuring (%d, %d)'s long pulse..." % (port_tx, port_rx))
        file_name = 'pulses_long/%02d_%02d_%d.csv' % (port_tx, port_rx, sps)
        with open(str(Path(file_name).resolve()), 'w', newline='') as f:
            writer = csv.writer(f)
            for signal in radar_signal[pulse_start_idx:pulse_start_idx + length_long]:
                writer.writerow([signal])
        print("Long index is %d" % pulse_start_idx)

        if is_print:
            self._data_mani_module.graphing_1D(arr_x=[[np.arange(length_long)]], arr_y=[[radar_signal[pulse_start_idx:pulse_start_idx + length_long]]])

        print("MAXIMUM VALUE IS %f" % (np.max(radar_signal)))
        return radar_signal, [pulse_start_idx, length_short, length_long]

    def measure_offset_signal(self, port_tx, port_rx, averaging_factor: int = 1):

        self._tx_switch.set_switch_port(port_tx)
        self._rx_switch.set_switch_port(port_rx)
        print("Measuring Pulse signal...")

        sum_radar_signal = 0
        for j in range(averaging_factor):
            radar_signal = self._radar.get_frame_normalized_double()
            for i in range(4):
                radar_signal[i * 512:i * 512 + 512] = radar_signal[i * 512:i * 512 + 512] - np.mean(
                    radar_signal[i * 512:i * 512 + 512])
            sum_radar_signal = radar_signal + sum_radar_signal

        sum_radar_signal = np.divide(sum_radar_signal, averaging_factor)

        sps = int(round(self._radar.get_samples_per_second(), 0))

        file_name = 'OffsetSignal_%02d_%02d_%d.csv' % (port_tx, port_rx, sps)

        print("Measuring (%d, %d)'s Offset pulse..." % (port_tx, port_rx))
        print("Printing...")
        with open(str(Path(file_name).resolve()), 'w', newline='') as f:
            writer = csv.writer(f)
            for signal in sum_radar_signal:
                writer.writerow([signal])

        return sum_radar_signal

    def is_matched_filtered(self):
        return self._radar_pulse_stretched is not None