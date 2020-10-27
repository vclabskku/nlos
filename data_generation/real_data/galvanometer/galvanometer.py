
import numpy as np
import nidaqmx
import math





class Galvanometer():

    def __init__(self, config):

        self.config = config

        self.task = nidaqmx.Task()
        # add x-axis channel
        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        # add y-axis channel
        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao1")

        self.width = 135
        self.height = 64

        self.num_grid = self.config["num_grid"] # num_grid x num_grid scanning
        self.voltage_range = self.config["voltage_range"] # [-max_voltage, max_voltage]

        self.x_term = self.width / self.num_grid
        self.y_term = self.height / self.num_grid

        self.absolute_x = 0
        self.absolute_y = 0

        self.voltages = np.linspace(self.voltage_range[0], self.voltage_range[1], self.num_grid)
        self.count = 0

    def calculate_x_voltage(self, x):
        a = -0.39500711
        b = 18.9413809
        self.absolute_x = 237 - x
        return a * math.degrees(math.atan(self.absolute_x / 120)) + b

    def calculate_y_voltage(self, y):
        a = -0.39680965
        self.absolute_y = 32 - y

        return a * math.degrees(math.atan(self.absolute_y / math.sqrt(120 ** 2 + self.absolute_x ** 2)))



    def step(self):

        x_index = self.count // self.num_grid
        y_index = self.count % self.num_grid

        x_voltage = self.calculate_x_voltage(x_index * self.x_term)
        y_voltage = self.calculate_y_voltage(y_index * self.y_term)

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