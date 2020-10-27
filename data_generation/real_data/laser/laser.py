import os

# if the code works normally, the return value is 0
class Laser():
    def __init__(self, config):
        self.config = config

    def turn_on(self):
        result = os.system(
            'C:/Users/vclab/PycharmProjects/nlos/data_generation/real_data/laser/laser_power2/Debug/laser_power2.exe {} {} {} {} {}'.format(
                int(self.config['cport_nr']), int(self.config['bdrate']),
                int(self.config['laser1']), int(self.config['laser2']),
                int(self.config['laser3'])))
        return result

    def turn_off(self):
        result = os.system(
            'C:/Users/vclab/PycharmProjects/nlos/data_generation/real_data/laser/laser_power2/Debug/laser_power2.exe {} {} {} {} {}'.format(
                int(self.config['cport_nr']), int(self.config['bdrate']),
                int(0), int(0), int(0)))
        return result