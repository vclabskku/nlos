from yeelight import Bulb
 
class Light():

    def __init__(self, config):

        self.config = config

        # initialize light bulbs
        self.bulb_list = [ Bulb(bulb_ip) for bulb_ip in config.LIGHT.BULB_LIST]

    def light_for_gt(self):

        gt_brightness = self.config["gt_brightness"]
        # set the lights to the specified brightness
        for bulb in bulb_list:
            bulb.set_brightness(gt_brightness) 

    def light_for_laser(self):

        laser_brightness = self.config["laser_brightness"]
        # set the lights to the specified brightness
        for bulb in bulb_list:
            bulb.set_brightness(laser_brightness) 

