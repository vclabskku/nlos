from data_generation.real_data.collect import Collector
import os

config = dict()

config["data_config"] = dict()

# 0.6, -0.6, 0.0
config["turtlebot_config"] = dict()
################################################################################
# Important Parameters
################################################################################
config["data_config"]["root_folder"] = "d:\\2022"
config["data_config"]["dst_folder"] = os.path.join(config["data_config"]["root_folder"],
                                                   "dummy") # Modify this as the target name (e.g., P, P_B ...)
config["turtlebot_config"]["num_turtlebots"] = 2
config["turtlebot_config"]["initial_indices"] = 0
config["sensor_config"] = dict()
config["sensor_config"]["use_laser"] = True
config["sensor_config"]["use_rf"] = True
config["sensor_config"]["use_sound"] = True
config["data_config"]["log_folder"] = os.path.join(config["data_config"]["root_folder"], "log")
################################################################################
# X: 0.6, -0.6
# leftbottom: 0.6, -1.0, 0.0
# righttop: 2.1, -2.1, 0.0
# config["turtlebot_config"]["area_range"] = [[0.0, -0.6], [1.6, -1.6]]
# config["turtlebot_config"]["area_range"] = [[1.0, -1.0], [2.0, -2.0]]
config["turtlebot_config"]["area_range"] = [[0.80, -0.80], [2.80, -2.40]]
config["turtlebot_config"]["angle_range"] = [0.0, 180.0]
if config["turtlebot_config"]["num_turtlebots"] <= 1:
    config["turtlebot_config"]["spatial_step"] = 0.30 # default 0.3
    config["turtlebot_config"]["angle_step"] = 30.0 # max 180, default 30.0
else:
    config["turtlebot_config"]["spatial_step"] = 0.80 # default 0.8
    config["turtlebot_config"]["angle_step"] = 90.0 # max 180, default 180.0
config["turtlebot_config"]["min_distance"] = 0.35
config["turtlebot_config"]["master_ip"] = "192.168.50.192"
# config["turtlebot_config"]["num_turtlebots"] = len(config["turtlebot_config"]["initial_indices"])
config["turtlebot_config"]["dummy_points"] = [[0.0, -2.0], [0.0, -2.0]]
'''
turtlebot config 추가
'''
config["turtlebot_config"]["using_list"] = ['{}'.format(i + 1)
                                            for i in range(config["turtlebot_config"]["num_turtlebots"])]
config["turtlebot_config"]["1"] = dict()
config["turtlebot_config"]["2"] = dict()
#### 22/04/15 Turetlebot 1 의 원인 모를 잦은 에러로 인해 Turtlebot2 로 변경
### 이에 따라 코드 변경은
# 1. config turtlebot_config, roscores [1] <-> [2] 변경
# 2. config pot 11311 <-> 11312
# 3. turtlebot 2의 map 2 -> map1
# 4. turtlebot command() function call 할때 single turtlebot 사용시 port 아규멘트 전달하는 인자 추가.

turtlebot_reverse = False
if turtlebot_reverse:
    turtlebot_map = ["2", "1"]
else:
    turtlebot_map = ["1", "2"]

config["turtlebot_config"]["ports"] = ["11311", "11312"]
if turtlebot_reverse:
    config["turtlebot_config"]["ports"] = config["turtlebot_config"]["ports"][::-1]
config["turtlebot_config"][turtlebot_map[0]]["ip"] = '192.168.50.124'
config["turtlebot_config"][turtlebot_map[0]]["username"] = 'ubuntu'
config["turtlebot_config"][turtlebot_map[0]]["password"] = 'vclab201703'
config["turtlebot_config"][turtlebot_map[0]]["roslanuch"] = 'roslaunch turtlebot3_bringup turtlebot3_robot.launch'

config["turtlebot_config"][turtlebot_map[1]]["ip"] = '192.168.50.55'
config["turtlebot_config"][turtlebot_map[1]]["username"] = 'ubuntu'
config["turtlebot_config"][turtlebot_map[1]]["password"] = 'vclab201703'
config["turtlebot_config"][turtlebot_map[1]]["roslanuch"] = 'roslaunch turtlebot3_bringup turtlebot3_robot.launch'

'''
roscore config 추가 
'''
config["roscore"] = dict()
config["roscore"]["1"] = dict()
config["roscore"]["2"] = dict()
config["roscore"]["1"]["terminal_1"] = dict()
config["roscore"]["1"]["terminal_2"] = dict()
config["roscore"]["2"]["terminal_1"] = dict()
config["roscore"]["2"]["terminal_2"] = dict()
config["roscore"][turtlebot_map[0]]["terminal_1"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "roscore --port 11311"
config["roscore"][turtlebot_map[0]]["terminal_2"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "set ROS_MASTER_URI=http://192.168.50.192:11311/ && " \
                                                    "roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c://ws//maps//map_0{}.yaml".format(turtlebot_map[0])
config["roscore"][turtlebot_map[1]]["terminal_1"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "roscore --port 11312"
config["roscore"][turtlebot_map[1]]["terminal_2"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "set ROS_MASTER_URI=http://192.168.50.192:11312/ && " \
                                                    "roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c://ws//maps//map_0{}.yaml".format(turtlebot_map[1])

#### Camera ID #####
# DEV_000F310382ED (Reflection Low) #
# DEV_000F310382EC (GT)#
# DEV_000F310382EB (Reflection High #
####################
config["cmos_config"] = dict()
config["cmos_config"]["cam_ids"] = ["DEV_000F310382EB", "DEV_000F310382ED"]
config["cmos_config"]["iterations"] = 3
config["cmos_config"]["exposure_time"] = 5.0e+5 # micro seconds
# config["cmos_config"]["exposure_time"] = 5.0e+3 # micro seconds
config["cmos_config"]["timeout_time"] = int(5.0e+3) # milli seconds

config["depth_config"] = dict()
config["depth_config"]["something"] = None

# If the port number of window is COM1, the cport_nr is 0
# The bdrate must be 9600
# The laser power must be 0 to 100
config["laser_config"] = dict()
config["laser_config"]["cport_nr"] = 2
config["laser_config"]["bdrate"] = 9600
config["laser_config"]["laser1"] = 100
config["laser_config"]["laser2"] = 76
config["laser_config"]["laser3"] = 85

# config["laser_config"]["laser1"] = 5
# config["laser_config"]["laser2"] = 5
# config["laser_config"]["laser3"] = 5

config["galvanometer_config"] = dict()
config["galvanometer_config"]["num_grid"] = 5
config["galvanometer_config"]["voltage_range"] = [-10.0, 10.0]

# config for light
config["light_config"] = dict()
# �޾�, ����, �޵�, ����
# config["light_config"]["bulb_list"] = ["192.168.50.61", "192.168.50.62", "192.168.50.175", "192.168.50.39"]
config["light_config"]["bulb_list"] = ["192.168.50.61", "192.168.50.62"]
config["light_config"]["gt_brightness"] = 100
config["light_config"]["laser_brightness"] = 1

# config for detector
config["detector_config"] = dict()
config["detector_config"]["detectron_root"] = "C:\\Users\\vclab\\PycharmProjects\\detectron2"
config["detector_config"]["config_file"] = "configs/novel/retinanet_R_50_FPN_1x.yaml"
config["detector_config"]["check_point"] = "output/novel/model_0004999.pth"

'''
음장 센서 관련 부분
'''
# # config for arduino
# config['arduino_config'] = dict()
# config['arduino_config']['port'] = "COM5"
# config['arduino_config']['baudrate'] = 9600
#
# # config for echo
# config["echo_config"] = dict()
# config["echo_config"]["device"] = "ASIO4ALL v2"
# config["echo_config"]["samplerate"] = 48000
# config["echo_config"]["bit_depth"] = "float32"
# config["echo_config"]["input_mapping"] = [1, 2, 3, 4, 5, 6, 7, 8]
# config["echo_config"]["output_mapping"] = [1, 2]
#
# config['echo_config']['amplitude'] = 1
# config['echo_config']['frequency'] = [20, 20000]
# config['echo_config']['transmit_duration'] = 0.1
# config['echo_config']['record_duration'] = 1
#
# config['echo_config']['folder_path'] = 'sound/data/'


'''
    소켓 통신 관련 config
'''

server = dict()
server['ip'] = "192.168.50.174"
server['port'] = 8888

config['server'] = server

if __name__ == '__main__':
    collector = Collector(config)
    # collector.initialize()
    collector.collect()
