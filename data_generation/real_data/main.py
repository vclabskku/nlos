from data_generation.real_data.collect import Collector

config = dict()

config["data_config"] = dict()
config["data_config"]["dst_folder"] = "./"
config["data_config"]["object_type"] = "human"

config["light_config"] = dict()
config["light_config"]["gt_brightness"] = 100
config["light_config"]["laser_brightness"] = 0

config["turtlebot_config"] = dict()
config["turtlebot_config"]["area_range"] = [[0.9, 0.0], [2.0, -2.0]]
config["turtlebot_config"]["angle_range"] = [0.0, 180.0]
config["turtlebot_config"]["spatial_step"] = 0.1
config["turtlebot_config"]["angle_step"] = 20.0

config["cmos_config"] = dict()
config["cmos_config"]["something"] = None

config["depth_config"] = dict()
config["depth_config"]["something"] = None

config["detector_config"] = dict()
config["detector_config"]["something"] = None

# If the port number of window is COM1, the cport_nr is 0
# The bdrate must be 9600
# The laser power must be 0 to 100
config["laser_config"] = dict()
config["laser_config"]["cport_nr"] = 2
config["laser_config"]["bdrate"] = 9600
config["laser_config"]["laser1"] = 100
config["laser_config"]["laser2"] = 100
config["laser_config"]["laser3"] = 100

config["galvanometer_config"] = dict()
config["galvanometer_config"]["num_grid"] = 7
config["galvanometer_config"]["voltage_range"] = [-10.0, 10.0]

# config for light
config["LIGHT"] = dict()
# �޾�, ����, �޵�, ����
config["LIGHT"]["BULB_LIST"] = ["192.168.50.61", "192.168.50.62", "192.168.50.175", "192.168.50.39"]
config["LIGHT"]["gt_brightness"] = 100
config["LIGHT"]["laser_brightness"] = 1

# config for detector
config["DETECTOR"] = dict()
config["DETECTOR"]["DETECTRON_ROOT"] = "C:\\Users\\vclab\\PycharmProjects\\detectron2"
config["DETECTOR"]["CONFIG_FILE"] = "configs/novel/retinanet_R_50_FPN_1x.yaml"
config["DETECTOR"]["CHECK_POINT"] = "output/novel/model_0004999.pth"

collector = Collector(config)
collector.collect()
