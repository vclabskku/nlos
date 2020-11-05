from data_generation.real_data.collect import Collector

config = dict()

config["data_config"] = dict()
config["data_config"]["dst_folder"] = "d:\\human_02"
config["data_config"]["object_type"] = "human"
# 0.6, -0.6, 0.0
config["turtlebot_config"] = dict()
config["turtlebot_config"]["area_range"] = [[0.6, -0.6], [2.0, -2.0]]
config["turtlebot_config"]["angle_range"] = [0.0, 10.0]
config["turtlebot_config"]["spatial_step"] = 0.1
config["turtlebot_config"]["angle_step"] = 20.0

#### Camera ID #####
# DEV_000F310382ED (Reflection Low) #
# DEV_000F310382EC (GT)#
# DEV_000F310382EB (Reflection High #
####################
config["cmos_config"] = dict()
config["cmos_config"]["cam_ids"] = ["DEV_000F310382EB", "DEV_000F310382ED"]
config["cmos_config"]["iterations"] = 3
config["cmos_config"]["exposure_time"] = 2.0e+6 # micro seconds
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

config["galvanometer_config"] = dict()
config["galvanometer_config"]["num_grid"] = 2
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

collector = Collector(config)
# collector.initialize()
collector.collect()
