from yeelight import Bulb
 
class Light():

    def __init__(self, config):

        self.config = config

        # initialize light bulbs
        self.bulb_list = [Bulb(bulb_ip) for bulb_ip in self.config["bulb_list"]]

    def light_for_gt(self):

        gt_brightness = self.config["gt_brightness"]
        # set the lights to the specified brightness
        for bulb in self.bulb_list:
            bulb.turn_on()
            bulb.set_brightness(gt_brightness) 

    def light_for_laser(self):

        laser_brightness = self.config["laser_brightness"]
        # set the lights to the specified brightness
        for bulb in self.bulb_list:
            # bulb.set_brightness(laser_brightness)
            bulb.turn_off()


if __name__ == '__main__': 
    import sys
    config = dict()
    #config for light
    config = dict()
    config["bulb_list"] = ["192.168.50.61", "192.168.50.62", "192.168.50.175", "192.168.50.39"]
    config["gt_brightness"] = 100
    config["laser_brightness"] = 0
    print(config)
    lo = Light(config)
    lo.light_for_gt()
    # lo.light_for_laser()
    # if sys.argv[1] == "gt":
    #     lo.light_for_gt()
    # elif sys.argv[1] == "laser":
    #     lo.light_for_laser()



