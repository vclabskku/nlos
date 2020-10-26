import os

class Laser():

    def __init__(self, config):
        self.config = config

    def laser_on(self):
        laser.change_power(100, 100, 100)

    def laser_off(self):
        laser.change_power(0, 0, 0)

    def change_power(self, laser_power1, laser_power2, laser_power3):
        result = os.system(
            'C:/Users/vclab/PycharmProjects/nlos/data_generation/real_data/laser/laser_power2/Debug/laser_power2.exe {} {} {} {} {}'.format(
                int(self.config['cport_nr']), int(self.config['bdrate']), int(laser_power1), int(laser_power2), int(laser_power3)))
        return result

config = dict(cport_nr=2, bdrate=9600)
laser = Laser(config)
temp = laser.change_power(0, 0, 0)
