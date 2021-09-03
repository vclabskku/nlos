from data_generation.real_data.collect import Collector

config = dict()

config["data_config"] = dict()
config["data_config"]["dst_folder"] = "d:\\human_04" # human_02
config["data_config"]["object_type"] = "human" # human
# 0.6, -0.6, 0.0
config["turtlebot_config"] = dict()
# string with 0! (You have to subtract 1 to wanted number!)
config["turtlebot_config"]["initial_index"] = 536 - 1
# X: 0.6, -0.6
# leftbottom: 0.6, -1.0, 0.0
# righttop: 2.1, -2.1, 0.0
# config["turtlebot_config"]["area_range"] = [[0.0, -0.6], [1.6, -1.6]]
config["turtlebot_config"]["area_range"] = [[0.6, -1.0], [2.1, -2.1]]
config["turtlebot_config"]["angle_range"] = [0.0, 180.0]
config["turtlebot_config"]["spatial_step"] = 0.1
config["turtlebot_config"]["angle_step"] = 60.0
'''
turtlebot config 추가
'''
config["turtlebot_config"]["using_list"] = ['1']
config["turtlebot_config"]["1"] = dict()
config["turtlebot_config"]["2"] = dict()
config["turtlebot_config"]["1"]["ip"] = '192.168.50.116'
config["turtlebot_config"]["1"]["username"] = 'turtlebot-01'
config["turtlebot_config"]["1"]["password"] = 'vclab201703'
config["turtlebot_config"]["1"]["roslanuch"] = 'roslaunch turtlebot3_bringup turtlebot3_robot.launch'
config["turtlebot_config"]["1"]["complete"] = True

config["turtlebot_config"]["2"]["ip"] = '192.168.50.55'
config["turtlebot_config"]["2"]["username"] = 'ubuntu'
config["turtlebot_config"]["2"]["password"] = 'vclab201703'
config["turtlebot_config"]["2"]["roslanuch"] = 'roslaunch turtlebot3_bringup turtlebot3_robot.launch'
config["turtlebot_config"]["1"]["complete"] = True

'''
roscore config 추가 
'''
# turtlebot을 직접 조작하는 terminal 명령어(terminal_2) 추가해야함..
# roscore의 set_master_uri의 ip 주소 확인 필요
config["roscore"] = dict()
config["roscore"]["1"] = dict()
config["roscore"]["2"] = dict()
config["roscore"]["1"]["terminal_1"] = dict()
config["roscore"]["1"]["terminal_2"] = dict()
config["roscore"]["2"]["terminal_1"] = dict()
config["roscore"]["2"]["terminal_2"] = dict()
config["roscore"]["1"]["terminal_1"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "roscore --port 11311"
config["roscore"]["1"]["terminal_1"]["complete"] = True
config["roscore"]["1"]["terminal_2"]["operation"] = "set ROS_MASTER_URI=http://192.168.50.192:11311/ && " \
                                                    "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c:\ws\maps\map_01.yaml"
config["roscore"]["1"]["terminal_2"]["complete"] = True
config["roscore"]["2"]["terminal_1"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "roscore --port 11312"
config["roscore"]["2"]["terminal_1"]["complete"] = True
config["roscore"]["2"]["terminal_2"]["operation"] = "set ROS_MASTER_URI=http://192.168.50.192:11312/ && " \
                                                    "set ChocolateyInstall=c://opt//chocolatey && " \
                                                    "c://opt//ros//melodic//x64//setup.bat && " \
                                                    "c://ws//turtlebot3//devel//setup.bat && " \
                                                    "roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c:\ws\maps\map_01.yaml"
config["roscore"]["2"]["terminal_2"]["complete"] = True



#### Camera ID #####
# DEV_000F310382ED (Reflection Low) #
# DEV_000F310382EC (GT)#
# DEV_000F310382EB (Reflection High #
####################
config["cmos_config"] = dict()
config["cmos_config"]["cam_ids"] = ["DEV_000F310382EB", "DEV_000F310382ED"]
config["cmos_config"]["iterations"] = 3
config["cmos_config"]["exposure_time"] = 5.0e+5 # micro seconds
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
config["light_config"]["bulb_list"] = ["192.168.50.61", "192.168.50.62", "192.168.50.175", "192.168.50.39"]
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

collector = Collector(config)
# collector.initialize()
collector.collect()
