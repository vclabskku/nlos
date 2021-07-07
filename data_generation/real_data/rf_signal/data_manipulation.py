import numpy as np
import matplotlib.pyplot as plt
from math import pi
import math, os, datetime


class data_manipulation_module:
    def __init__(self):
        self.a = 1
        self.list_x = None
        self.list_y = None

    def init_graph_list(self):
        self.list_x = []
        self.list_y = []

    def add_graph_list(self, element_x, element_y):
        self.list_x.append(element_x)
        self.list_y.append(element_y)

    #   단순히 배열의 길이를 늘리기만 한다.
    #   나머지 부분은 0으로 채운다.
    def data_stretched_no_modify(self, data :np.ndarray, target_length :int):
        self.a = 1
        if data.size < target_length:
            print("sizes are wrong")
            return -1

        ret = np.zeros(target_length)
        ret[:data.size] = data

        return ret

    #   np.interp 와 비슷한 연산을 한다.
    #   interp 와 다르게, origin_axis 범위 밖의 모든 부분들을 0으로 채운다.
    #       interp 는 낮은 부분들만 0으로 채운다.
    #   target_axis
    #       -   y 값을 구할 x 축 좌표들이다.
    #       -   순서에 상관이 없다
    #   origin_axis
    #       -   기존의 x 축 좌표들이다.
    #       -   x[i] <= x[j] for all i <= j
    #   data
    #       -   기존의 y 축 좌표들이다.
    #       -   origin_axis 와 크기가 같아야 한다.
    def data_interp_zeros(self, target_axis :np.ndarray, origin_axis :np.ndarray, data :np.ndarray):
        self.a = 1
        # if data.size is not origin_axis.size:
        #     print("DataManipulation__data_interp_zeros : origin data sizes are wrong %d %d" % (data.size, origin_axis.size))

        return np.interp(target_axis, origin_axis, data) * ((origin_axis[0] <= target_axis) & (target_axis <= origin_axis[-1]))

    #   측정 데이터의 시간 영역과 주파수 영역의 x 축 좌표들의 배열을 구한다.
    #   시간 영역
    #       - N or n : Nano seconds
    #       - U or u : Micro seconds
    #       - M or m : Mili
    #   주파수 영역
    #       - G or g : Giga
    #       - M or m : Mega
    #       - K or k : Kilo
    def get_sample_spacing(self, samples_per_second :int, size :int, unit_output_time :str, unit_output_freq :str):
        self.a = 1

        if unit_output_time[0] == 'N' or unit_output_time[0] == 'n':
            u_output_time = 1e9
        elif unit_output_time[0] == 'U' or unit_output_time[0] == 'u':
            u_output_time = 1e6
        elif unit_output_time[0] == 'M' or unit_output_time[0] == 'm':
            u_output_time = 1e3
        else:
            u_output_time = 1

        if unit_output_freq[0] == 'G' or unit_output_freq[0] == 'g':
            u_output_freq = 1e-9
        elif unit_output_freq[0] == 'M' or unit_output_freq[0] == 'm':
            u_output_freq = 1e-6
        elif unit_output_freq[0] == 'K' or unit_output_freq[0] == 'u':
            u_output_freq = 1e-3
        else:
            u_output_freq = 1

        ret_time = np.arange(size) * u_output_time / samples_per_second
        ret_freq = np.arange(size) * u_output_freq * samples_per_second / size

        return ret_time, ret_freq

    #   신호 데이터의 시간 영역 혹은 주파수 영역의 x축 단위를 샘플의 개수를 유지하면서 변환한다.
    #   시간영역의 단위가 변하면 주파수 영역도 그에 따라서 변하도록 한다.
    #   주파수 영역의 단위가 바뀌면 시간 영역의 단위도 그에 따라서 바뀐다.
    #
    #   time_x : 변환 전 시간 영역의 x 좌표
    #   freq_x : 변환 전 주파수 영역의 x 좌표
    #   delta_before : 변환 전 단위의 크기(ex: 10MHz 에서 10)
    #   delta_after : 변환 후 단위의 크기
    #   unit_before : 변환 전 단위(ex: 10MHz 에서 MHz, 8.2ms 에서 ms), unit_after 와 시간 or 주파수가 일치해야됨
    #   unit_after : 변환 후 단위 unit_before 와 시간 or 주파수가 일치해야됨
    def get_new_sample_spacing(self, time_x :np.ndarray, freq_x :np.ndarray, delta_before :float, delta_after :float, unit_before :str, unit_after :str):

        if unit_before[0] == 'H' or unit_before[0] == 'h' or unit_before[1] == 'H' or unit_before[1] == 'h':
            mode_is_freq = True
        elif unit_before[0] == 'S' or unit_before[0] == 'S' or unit_before[1] == 'S' or unit_before[1] == 's':
            mode_is_freq = False
        else:
            print("unit_before is wrong")
            return None

        if (unit_after[0] == 'H' or unit_after[0] == 'h' or unit_after[1] == 'H' or unit_after[1] == 'h') and (mode_is_freq is False) is True:
            print("Input : time, Output : freq -> Wrong")
            return None
        elif (unit_after[0] == 'S' or unit_after[0] == 'S' or unit_after[1] == 'S' or unit_after[1] == 's') and (mode_is_freq is True) is True:
            print("Input : freq, Output : time -> Wrong")
            return None

        if mode_is_freq:
            if unit_before[0] == 'G' or unit_before[0] == 'g':
                c = 1000
            elif unit_before[0] == 'M' or unit_before[0] == 'm':
                c = 1
            elif unit_before[0] == 'K' or unit_before[0] == 'k':
                c = 0.001
            elif unit_before[0] == 'H' or unit_before[0] == 'h':
                c = 0.000001
            else:
                print("Unit of frequency is too small")
                return None

            if unit_after[0] == 'G' or unit_after[0] == 'g':
                d = 0.001
            elif unit_after[0] == 'M' or unit_after[0] == 'm':
                d = 1
            elif unit_after[0] == 'K' or unit_after[0] == 'k':
                d = 1000
            elif unit_after[0] == 'H' or unit_after[0] == 'h':
                d = 1000000
            else:
                print("Unit of frequency is too small")
                return None

            ret_freq = freq_x * c * d * delta_after / delta_before
            ret_time = time_x * delta_before / (c * d * delta_after)

        else:
            if unit_before[0] == 'P' or unit_before[0] == 'p':
                c = 0.000001
            elif unit_before[0] == 'N' or unit_before[0] == 'n':
                c = 0.0001
            elif unit_before[0] == 'U' or unit_before[0] == 'u':
                c = 1
            elif unit_before[0] == 'M' or unit_before[0] == 'm':
                c = 1000
            elif unit_before[0] == 'S' or unit_before[0] == 's':
                c = 1000000
            else:
                print("Unit of time is too large")
                return None

            if unit_before[0] == 'P' or unit_before[0] == 'p':
                d = 1000000
            elif unit_before[0] == 'N' or unit_before[0] == 'n':
                d = 1000
            elif unit_before[0] == 'U' or unit_before[0] == 'u':
                d = 1
            elif unit_before[0] == 'M' or unit_before[0] == 'm':
                d = 0.001
            elif unit_before[0] == 'S' or unit_before[0] == 's':
                d = 0.000001
            else:
                print("Unit of time is too large")
                return None

            ret_time = time_x * c * d * delta_after / delta_before
            ret_freq = freq_x * delta_before / (c * d * delta_after)

        return ret_time, ret_freq

    def _resizing(self, x_t, y_t):
        self.a = 1
        x_size = x_t.size
        y_size = y_t.size

        if x_size > y_size:
            z = np.zeros(x_size)
            z[:y_size] = y_t
            return x_t, z
        elif x_size < y_size:
            z = np.zeros(y_size)
            z[:x_size] = x_t
            return z, y_t
        else:
            return x_t, y_t

    def _return_mode(self, data, mode: str=None):
        self.a = 1
        if mode is None:
            return data
        elif mode is "complex" or mode is "cpx":
            return np.real(data), np.imag(data)
        elif mode[:4] is "real":
            return np.real(data)
        elif mode[:4] is "imag":
            return np.imag(data)
        elif mode[:3] is "abs" or mode[:3] is "Abs":
            return np.abs(data)
        else:
            return data

    def convert_deconvolution(self, x_t, y_t, any_value, output_mode: str=None):
        x_t, y_t = self._resizing(x_t, y_t)

        x_f = np.fft.fft(x_t)
        y_f = np.fft.fft(y_t)
        x_f[0] = 1
        h_f = y_f / x_f
        h_t = np.fft.ifft(h_f)

        return self._return_mode(h_t, output_mode)

    def convert_selective_divide(self, x_t, y_t, threshold, output_mode: str=None):
        x_t, y_t = self._resizing(x_t, y_t)
        x_f = np.fft.fft(x_t)
        y_f = np.fft.fft(y_t)

        sizes = len(x_f)

        h_f = np.zeros(sizes)

        for i in range(sizes):
            if np.abs(x_f[i]) >= threshold:
                h_f[i] = y_f[i]/x_f[i]

        h_t = np.fft.ifft(h_f)

        return self._return_mode(h_t, output_mode)

    def convert_wiener_convolution(self, x_t, y_t, snr_dB, output_mode: str=None):
        x_t, y_t = self._resizing(x_t, y_t)

        x_f = np.fft.fft(x_t)
        y_f = np.fft.fft(y_t)
        snr = math.pow(10, snr_dB/10)
        g_f = np.conj(x_f) / (np.square(np.absolute(x_f)) + 1 / snr)
        h_f = y_f * g_f
        h_t = np.fft.ifft(h_f)

        return self._return_mode(h_t, output_mode)

    #   y_t 가 고정된다
    #   cor[0] = x_t[-1]*y_t[0] 이다.
    #       x_t 의 오른쪽 끝부분부터 y_t 의 선두 부분이랑 접촉을 시작한다.
    #   x_t 의 시작부분과 y_t 의 시작부분이 만나는 지점부터의 데이터가 의미가 있다.
    def convert_cross_correlation(self, x_t, y_t, output_mode: str=None):
        x_t, y_t = self._resizing(x_t, y_t)
        length = x_t.size
        h_cor = np.correlate(y_t, x_t, 'full')
        h_t = h_cor[length-1:]
        return self._return_mode(h_t, output_mode)

    def convert_filter_lpf_f(self, x_t, ff, output_mode: str=None):
        x_f = np.fft.fft(x_t)
        for i in range(ff, x_t.size):
            x_f[i] = 0
        x_t = np.fft.ifft(x_f)
        return self._return_mode(x_t, output_mode)

    def convert_filter_lpf_t(self, x_t, ff, output_mode: str=None):
        w0 = 2 * pi * ff
        fs = 1
        mothers = w0+2

        y_t = np.zeros(x_t.size)
        y_t[0] = 2*x_t[0]/mothers

        for i in range(1, x_t.size):
            y_t[i] = 2/mothers*x_t[i] - 2/mothers*x_t[i-1] - (w0-2)/mothers*y_t[i-1]

        return self._return_mode(y_t, output_mode)


    #   arr_x 는 arr_y 와 차원이 같아야 한다.
    #   arr_x 는 3차원 리스트이다
    #       (row, col, data)
    def graphing_1D(self, arr_x=None, arr_y=None, isDot :bool=False, isCpx :bool=False):

        if arr_x is None:
            arr_x = self.list_x
        if arr_y is None:
            arr_y = self.list_y

        if arr_x is None or arr_y is None:
            print("list_x and list_y should be filled")
            return None

        if len(arr_x) is not len(arr_y):
            print("size of row is different")
            return None

        if len(arr_x[0]) is not len(arr_y[0]):
            print("size of col is different")
            return None

        size_row = len(arr_x)
        size_col = len(arr_x[0])

        fig = plt.figure()

        for i in range(size_row):
            for j in range(size_col):
                t = fig.add_subplot(size_row, size_col, i*size_col + j + 1)
                if isCpx:
                    if isDot:
                        t.plot(arr_x[i][j], np.real(arr_y[i][j]), '.')
                        t.plot(arr_x[i][j], np.imag(arr_y[i][j]), '.')
                    else:
                        t.plot(arr_x[i][j], np.real(arr_y[i][j]))
                        t.plot(arr_x[i][j], np.imag(arr_y[i][j]))
                else:
                    if isDot:
                        t.plot(arr_x[i][j], arr_y[i][j], '.')
                    else:
                        t.plot(arr_x[i][j], arr_y[i][j])

        plt.show()

    def create_image_directory(self, base_dir: str):
        self.a = 1
        os.makedirs(base_dir, exist_ok=True)

        dtime = datetime.datetime.now()
        dtimes = '/%d_%d_%d' % (int(dtime.year), int(dtime.month), int(dtime.day))
        dir_name = base_dir + dtimes
        os.makedirs(dir_name, exist_ok=True)

        folder_count = len(os.listdir(dir_name))
        dir_name_2 = dir_name + dtimes + '_%d' % folder_count
        os.makedirs(dir_name_2, exist_ok=True)

        return dir_name_2 + '/'