
from data_generation.real_data.collect import Collector

config = dict()

config["data_config"] = dict()
config["data_config"]["dst_folder"] = "/mnt/hdd0"
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

config["laser_config"] = dict()
config["laser_config"]["something"] = None

config["galvanometer_config"] = dict()
config["galvanometer_config"]["num_grid"] = 7
config["galvanometer_config"]["voltage_range"] = [-10.0, 10.0]

Collector.collect(config)