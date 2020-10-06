
from data_generation.real_data.collect import Collector

config = dict()

config["data_config"] = dict()
config["data_config"]["dst_folder"] = "./"
config["data_config"]["object_type"] = "human"

config["light_config"] = dict()
config["light_config"]["gt_brightness"] = 100
config["light_config"]["laser_brightness"] = 0

config["turtlebot_config"] = dict()
config["turtlebot_config"]["area_range"] = [0.0, 0.0]

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
config["laser_config"]["laser1_power"] = 100
config["laser_config"]["laser2_power"] = 100
config["laser_config"]["laser3_power"] = 100


config["galvanometer_config"] = dict()
config["galvanometer_config"]["num_grid"] = 7
config["galvanometer_config"]["voltage_range"] = [-10.0, 10.0]

collector = Collector(config)
collector.collect()