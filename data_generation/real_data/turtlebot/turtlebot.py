import numpy as np
import subprocess
import math


class Turtlebot():

    def __init__(self, config):

        self.config = config
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_a = 0.0
        self.max_iterations = 10
        self.max_spatial_movement = 0.2
        self.max_angular_movement = 90.0

        x_min = self.config["area_range"][0][0]
        y_min = self.config["area_range"][0][1]
        x_max = self.config["area_range"][1][0]
        y_max = self.config["area_range"][1][1]
        a_min = self.config["angle_range"][0]
        a_max = self.config["angle_range"][1]
        s_step = self.config["spatial_step"]
        a_step = self.config["angle_step"]

        self.x_coords = np.arange(x_min, x_max + 1, s_step)
        self.y_coords = np.arange(y_min, y_max + 1, s_step)
        self.angles = list()
        for angle in range(a_min, a_max, a_step):
            self.angles.append(angle)
            self.angles.append(angle + 180.0)

        self.index = 0
        self.l_x = len(self.x_coords)
        self.l_y = len(self.y_coords)
        self.l_a = len(self.angles)

    def step(self):
        x = self.x_coords[self.index // (self.l_y * self.l_a)]
        y = self.y_coords[(self.index // (self.l_a)) % self.l_y]
        a = self.angles[self.index % self.l_a]
        while True:
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals " \
                "&& simple_navigation_goals.exe {} {} {}".format(x, y, a)
            ok = subprocess.check_output(cmd.split())
            ok = bool(ok.decode().rstrip())
            if ok:
                break
        self.current_x = x
        self.current_y = y
        self.current_a = a

        self.index += 1
        done = self.index >= self.l_x * self.l_y * self.l_a

        return done, [x, y, a]

    def move(self, target):
        c_x, c_y, c_a = self.current_x, self.current_y, self.current_a
        t_x, t_y, t_a = target

        # x movement
        if np.abs(t_x - c_x) >= self.max_spatial_movement:
            if t_x >= c_x:
                self.angular_move(0.0)
                steps = math.ceil(np.abs(t_x - c_x) / self.max_spatial_movement)


    def angular_move(self, target):
        c_x, c_y, c_a = self.current_x, self.current_y, self.current_a
        t_a = target

        if np.abs(t_a - c_a) > self.max_angular_movement:
            middle_a = (t_a + c_a) / 2.0
            self.command(c_x, c_y, middle_a)
        self.command(c_x, c_y, t_a)

    def command(self, x, y, a):
        count = 0
        while True:
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals " \
                "&& simple_navigation_goals.exe {} {} {}".format(x, y, a)
            ok = subprocess.check_output(cmd.split())
            ok = bool(ok.decode().rstrip())
            count += 1
            if ok or (count > self.max_iterations):
                break



if __name__ == "__main__":
    config = dict()
    config["area_range"] = [[0.0, 0.0], [10.0, 10.0]]
    config["angle_range"] = [0.0, 180.0]
    config["spatial_step"] = 0.1
    config["angle_step"] = 10.0

    turtlebot = Turtlebot(config=config)
