import os
import numpy as np
from data_generation.real_data.rf_signal.NatNetClient1 import NatNetClient
from data_generation.real_data.rf_signal.cam_control import Camera

# Setting radar system
num_tx_antenna = 4
num_rx_antenna = 4
radar_info = {'radar_lib_path': 'Radarlib3_API/Radarlib3.NET.dll',
              'band': 'low',
              'sample_delay_to_reference': 27,
              'offset_distance_from_reference': 0,
              'frame_stitch': 2,
              'gain': 3,
              'averaging_factor': 1,
              'iterations': 100,
              'zoom_min': 40,
              'zoom_max': 60}
switch_info = {'switch_lib_path': 'Switch_DLL/mcl_SolidStateSwitch64.dll',
               'tx_switch_serial_number': '11903140023',
               'rx_switch_serial_number': '11903140025'}
dir_pulse = './pulses_long4/'
snr_for_wiener_dB = -12
tx_antenna_position = np.array([[0, 0, 1.050],
                                [0, 0, 0.800],
                                [0, 0, 0.550],
                                [0, 0, 0.300],
                                # [0.5, 0, 1.050],
                                # [0.5, 0, 0.800],
                                # [0.5, 0, 0.550],
                                # [0.5, 0, 0.300]
                                ])
rx_antenna_position = np.array([[-0.500, 0, 0.800],
                                [-0.200, 0, 0.800],
                                [0.200, 0, 0.800],
                                [0.500, 0, 0.800],
                                # [-0.3, 0, 0.300],
                                # [-0.1, 0, 0.300],
                                # [0.1, 0, 0.300],
                                # [0.3, 0, 0.300]
                                ])
volume_min_point = np.array([-1.5, 0, -1])
volume_max_point = np.array([1.5, 3, 2])
volume_num_step = np.array([100, 100, 100])

image_dir = '____IMAGE/'
# os.makedirs(image_dir)
url = 'http://192.168.43.205:7778/shot.jpg'
username = 'justice'
password = 'neverdie'
camera = Camera(is_webcam=False, username=username, password=password, url=url, img_dir=image_dir)

streamingClient = NatNetClient()
streamingClient.set_radar_system(num_tx_antenna=num_tx_antenna, num_rx_antenna=num_rx_antenna, radar_info=radar_info,
                                 switch_info=switch_info, pulse_dir=dir_pulse, snr_for_wiener_dB=snr_for_wiener_dB,
                                 tx_antenna_position=tx_antenna_position, rx_antenna_position=rx_antenna_position,
                                 volume_min_point=volume_min_point, volume_max_point=volume_max_point,
                                 volume_num_step=volume_num_step, camera=camera)

streamingClient.run()
# streamingClient.radar_data(flag=1, camera=camera)