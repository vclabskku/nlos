import os

# if the code works normally, the return value is 0
class Laser():
    def __init__(self, config):
        self.config = config

    def turn_on(self, laser_number):
        result = os.system('./laser_on {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']), int(laser_number)))
        return result

    def turn_off(self, laser_number):
        result = os.system('./laser_off {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']), int(laser_number)))
        return result

    def change_power(self, laser_number):
        if laser_number == 1:
            result = os.system(
                './laser_power {] {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']),
                                                   int(laser_number), int(self.config['laser1_power'])))
            return result
        elif laser_number == 2:
            result = os.system(
                './laser_power {] {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']),
                                                   int(laser_number), int(self.config['laser2_power'])))
            return result
        elif  laser_number == 3:
            result = os.system(
                './laser_power {] {} {} {}'.format(int(self.config['cport_nr']), int(self.config['bdrate']),
                                                   int(laser_number), int(self.config['laser3_power'])))
            return result
        else:
            return -1