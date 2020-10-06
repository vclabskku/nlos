import os

class Laser():
    def __init__(self, config):
        self.config = config

    def turn_on(self, laser_number):
        result = os.system('./laser_on {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']), int(laser_number)))
        return result

    def turn_off(self, laser_number):
        result = os.system('./laser_off {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']), int(laser_number)))
        return result

    def change_power(self, laser_number, laser_power):
        result = os.system('./laser_power {] {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']), int(laser_number), int(laser_power)))
        return result


config = dict(cport_nr=2, bdrate=9600)
laser = Laser(config)
temp = laser.turn_on(1)
if temp != 0:
    print("fail")
    exit()
else:
    temp = laser.change_power(1, 10)
    if temp !=0:
        print("fail")
        exit()