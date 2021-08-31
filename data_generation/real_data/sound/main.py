from collect import Collector

config = dict()

# config for arduino
config['arduino_config'] = dict()
config['arduino_config']['port'] = "COM5"
config['arduino_config']['baudrate'] = 9600

# config for echo
config["echo_config"] = dict()
config["echo_config"]["device"] = "ASIO4ALL v2"
config["echo_config"]["samplerate"] = 48000
config["echo_config"]["bit_depth"] = "float32"
config["echo_config"]["input_mapping"] = [1, 2, 3, 4, 5, 6, 7, 8]
config["echo_config"]["output_mapping"] = [3, 4]

config['echo_config']['amplitude'] = 1
config['echo_config']['frequency'] = [20, 20000]
config['echo_config']['transmit_duration'] = 0.1
config['echo_config']['record_duration'] = 1

config['echo_config']['folder_path'] = 'sound/data/'

collector = Collector(config)
# collector.initialize()
collector.collect()
