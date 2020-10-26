
import numpy as np
import nidaqmx
import math

def calculate_x_voltage(x):
    a = -0.39669946
    b = 19.5017455
    return a*math.degrees(math.atan((279-x)/166))+b

def calculate_y_voltage(y):
    a = -0.39294275
    b = -0.043263
    return a*math.degrees(math.atan((44.5-y)/252))+b



class Galvanometer():

    def __init__(self, config):

        self.config = config

        self.task = nidaqmx.Task()
        # add x-axis channel
        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        # add y-axis channel
        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao1")

        self.width = 187
        self.height = 90.5

        self.num_grid = self.config["num_grid"] # num_grid x num_grid scanning
        self.voltage_range = self.config["voltage_range"] # [-max_voltage, max_voltage]

        self.x_term = self.width / self.num_grid
        self.y_term = self.height / self.num_grid

        self.voltages = np.linspace(self.voltage_range[0], self.voltage_range[1], self.num_grid)
        self.count = 0



    def step(self):

        x_index = self.count // self.num_grid
        y_index = self.count % self.num_grid

        x_voltage = calculate_x_voltage(x_index * self.x_term)
        y_voltage = calculate_y_voltage(y_index * self.y_term)

        print([x_voltage, y_voltage])

        self.task.write([x_voltage, y_voltage], auto_start=True)
        self.count += 1

        if self.count >= self.num_grid ** 2:
            self.task.close()
            return True, [x_index, y_index]
        else:
            return False, [x_index, y_index]

if __name__ == "__main__":
    config = dict()
    config["galvanometer_config"] = dict()
    config["galvanometer_config"]["num_grid"] = 7
    config["galvanometer_config"]["voltage_range"] = [-10.0, 10.0]
    print("~~")
    galv = Galvanometer(config["galvanometer_config"])
    print("!!")
    import time
    done = False
    while not done:
        print("!!")
        done, _ = galv.step()
        time.sleep(1)