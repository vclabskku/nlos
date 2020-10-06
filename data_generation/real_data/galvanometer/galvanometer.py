
import numpy as np
import nidaqmx

class Galvanometer():

    def __init__(self, config):

        self.config = config

        self.task = nidaqmx.Task()
        # add x-axis channel
        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        # add y-axis channel
        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao1")

        self.num_grid = self.config["num_grid"] # num_grid x num_grid scanning
        self.voltage_range = self.config["voltage_range"] # [-max_voltage, max_voltage]

        self.voltages = np.linspace(self.voltage_range[0], self.voltage_range[1], self.num_grid)
        self.count = 0

    def step(self):

        x_index = self.count // self.num_grid
        y_index = self.count % self.num_grid

        x_voltage = self.voltages[x_index]
        y_voltage = self.voltages[y_index]

        self.task.write([x_voltage, y_voltage])
        self.count += 1

        if self.count >= self.num_grid ** 2:
            self.task.close()
            return True, [x_index, y_index]
        else:
            return False, [x_index, y_index]