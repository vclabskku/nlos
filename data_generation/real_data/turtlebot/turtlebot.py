import numpy as np
import subprocess
import math
import os
import time
import psutil


class Turtlebot():

    def __init__(self, config):
        self.config = config

        self.num_turtlebots = self.config["num_turtlebots"]

        self.current_xs = [0.0] * self.num_turtlebots
        self.current_ys = [0.0] * self.num_turtlebots
        self.current_as = [0.0] * self.num_turtlebots

        self.max_iterations = 10
        self.max_time = 300.0
        self.min_spatial_movement = 0.1
        self.max_spatial_movement = 0.1
        self.min_angular_movement = 30.0
        self.max_angular_movement = 90.0

        x_min = self.config["area_range"][0][0]
        y_min = self.config["area_range"][0][1]
        x_max = self.config["area_range"][1][0]
        y_max = self.config["area_range"][1][1]
        a_min = self.config["angle_range"][0]
        a_max = self.config["angle_range"][1]
        s_step = self.config["spatial_step"]
        a_step = self.config["angle_step"]

        if x_max >= x_min:
            self.x_coords = np.arange(x_min, x_max + 1.0e-7, s_step)
        else:
            self.x_coords = np.arange(x_min, x_max - 1.0e-7, -s_step)

        if y_max >= y_min:
            self.y_coords = np.arange(y_min, y_max + 1.0e-7, s_step)
        else:
            self.y_coords = np.arange(y_min, y_max - 1.0e-7, -s_step)

        self.angles = list()
        for angle in np.arange(a_min, a_max, a_step):
            self.angles.append(angle)
            self.angles.append(angle + 180.0)

        self.ports = self.config["ports"]
        self.master_ip = self.config["master_ip"]
        self.l_x = len(self.x_coords)
        self.l_y = len(self.y_coords)
        self.l_a = len(self.angles)
        self.l = self.l_x * self.l_y * self.l_a
        self.initialized = False

        if self.num_turtlebots <= 1:
            self.indices = [self.config["initial_indices"]]
        else:
            self.indices = [self.config["initial_indices"] % self.l,
                            self.config["initial_indices"] // self.l]

    def step(self):
        # while True:
        #     cmd = \
        #         "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
        #         "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals " \
        #         "&& simple_navigation_goals.exe {} {} {}".format(x, y, a)
        #     ok = subprocess.check_output(cmd.split())
        #     ok = bool(ok.decode().rstrip())
        #     if ok:
        #         break

        # self.move(x, y, a)

        if self.num_turtlebots >= 2:
            if not self.initialized:
                # Initialize the 2nd turtlebot
                x = self.x_coords[-(self.indices[1] // (self.l_y * self.l_a)) - 1]
                y = self.y_coords[-((self.indices[1] // self.l_a) % self.l_y) - 1]
                a = self.angles[-(self.indices[1] % self.l_a) - 1]

                self.command(x, y + 1.0, a, port=self.ports[1])
                self.current_xs[1] = x
                self.current_ys[1] = y
                self.current_as[1] = a

                self.initialized = True

            # move the 1st turtlebot
            done = False
            while True:
                x = self.x_coords[self.indices[0] // (self.l_y * self.l_a)]
                y = self.y_coords[(self.indices[0] // (self.l_a)) % self.l_y]
                a = self.angles[self.indices[0] % self.l_a]

                x_distance = abs(x - self.current_xs[1])
                y_distance = abs(y - self.current_ys[1])

                if x_distance >= self.config["min_distance"] or y_distance >= self.config["min_distance"]:
                    # if the distances are far enough, move the 1st turtlebot
                    break

                # if the distances are not far enough, increment the index
                self.indices[0] += 1
                done = self.indices[0] >= self.l_x * self.l_y * self.l_a

                if done:
                    # if the distances are not far enough but the index is the end, move the 2nd turtlebot
                    break

            if not done:
                # move the 1st turtlebot
                self.command(x, y, a, port=self.ports[0])
                self.current_xs[0] = x
                self.current_ys[0] = y
                self.current_as[0] = a

                self.indices[0] += 1
                done = self.indices[0] >= self.l_x * self.l_y * self.l_a

            # move the 2nd turtlebot
            if done:
                # if the 1st turtlebot completes one cycle, move the 2nd turtlebot and initialize the 1st one
                self.indices[0] = 0

                # before move the 2nd, move the 1st to the dummy point to prevent collision
                x = self.config["dummy_points"][0]
                y = self.config["dummy_points"][1]
                a = 0.0

                self.command(x, y, a, port=self.ports[0])

                # move the 2nd turtlebot
                self.indices[1] += 1
                x = self.x_coords[-(self.indices[1] // (self.l_y * self.l_a)) - 1]
                y = self.y_coords[-((self.indices[1] // self.l_a) % self.l_y) - 1]
                a = self.angles[-(self.indices[1] % self.l_a) - 1]

                self.command(x, y + 1.0, a, port=self.ports[1])
                self.current_xs[1] = x
                self.current_ys[1] = y
                self.current_as[1] = a

                # move the 1st turtlebot to the init point
                x = self.x_coords[self.indices[0] // (self.l_y * self.l_a)]
                y = self.y_coords[(self.indices[0] // (self.l_a)) % self.l_y]
                a = self.angles[self.indices[0] % self.l_a]

                self.command(x, y, a, port=self.ports[0])
                self.current_xs[0] = x
                self.current_ys[0] = y
                self.current_as[0] = a

                self.indices[0] += 1
                done = self.indices[0] >= self.l_x * self.l_y * self.l_a

            done = done and (self.indices[1] >= self.l_x * self.l_y * self.l_a)
        else:
            x = self.x_coords[self.indices[0] // (self.l_y * self.l_a)]
            y = self.y_coords[(self.indices[0] // (self.l_a)) % self.l_y]
            a = self.angles[self.indices[0] % self.l_a]

            self.command(x, y, a, port=self.ports[0])
            self.current_xs[0] = x
            self.current_ys[0] = y
            self.current_as[0] = a

            self.indices[0] += 1
            done = self.indices[0] >= self.l_x * self.l_y * self.l_a

        return done, [self.current_xs, self.current_ys, self.current_as]

    def move(self, t_x, t_y, t_a):
        # x movement
        next_a = 0.0 if t_x >= self.current_x else 180.0
        self.command(self.current_x, self.current_y, next_a)
        self.current_a = next_a
        while True:
            if t_x >= self.current_x:
                next_x = self.current_x + self.max_spatial_movement
            else:
                next_x = self.current_x - self.max_spatial_movement
            if np.abs(next_x - t_x) <= self.min_spatial_movement:
                self.command(t_x, self.current_y, self.current_a)
                self.current_x = t_x
                break
            else:
                self.command(next_x, self.current_y, self.current_a)
                self.current_x = next_x

        # y movement
        next_a = 90.0 if t_y >= self.current_y else 270
        self.command(self.current_x, self.current_y, next_a)
        self.current_a = next_a
        while True:
            if t_y >= self.current_y:
                next_y = self.current_y + self.max_spatial_movement
            else:
                next_y = self.current_y - self.max_spatial_movement
            if np.abs(next_y - t_y) <= self.min_spatial_movement:
                self.command(self.current_x, t_y, self.current_a)
                self.current_y = t_y
                break
            else:
                self.command(self.current_x, next_y, self.current_a)
                self.current_y = next_y

        # a movement
        self.command(self.current_x, self.current_y, t_a)

    # def angular_move(self, target):
    #     t_a = target
    #
    #     if np.abs(t_a - self.current_a) > self.max_angular_movement:
    #         middle_a = (t_a + self.current_a) / 2.0
    #         self.command(self.current_x, self.current_y, middle_a)
    #     self.command(self.current_x, self.current_y, t_a)
    #     self.current_a = t_a
    #
    #     while True:
    #         if t_a <= 180.0:
    #             next_a = self.current_a + self.max_angular_movement
    #         else:
    #             next_a = self.current_a - self.max_angular_movement
    #         if np.abs(next_a - t_a) <= self.min_angular_movement:
    #             self.command(self.current_x, self.current_y, t_a)
    #             self.current_a = t_a
    #             break
    #         else:
    #             self.command(self.current_x, self.current_y, next_a)
    #             self.current_a = next_a   

    def command(self, x, y, a, port="11311"):
        count = 0
        while True:
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals && " \
                "set ROS_MASTER_URI=http://{}:{} && " \
                "simple_navigation_goals.exe {} {} {}".format(self.config["master_ip"], port, x, y, a)

            # ok = bool(os.system(cmd))

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            try:
                p.wait(self.max_time)
                ok = p.returncode
            except subprocess.TimeoutExpired:
                # p.kill()
                self.kill(p.pid)
                ok = False

            count += 1
            if ok:
                break
            else:
                self.escape(port=port)

            if count > self.max_iterations:
                print("ERROR: Turtlebot cannot move!!!!")
                print("Please move the turtlebot to [0, 0] and restart the navigation program!")
                exit()

            if count % 3 == 0:
                time.sleep(1)
                self.command(0, 0, 0)
                time.sleep(1)

    def kill(self, proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def escape(self, port="11311"):
        for _ in range(2):
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals_02 && " \
                "set ROS_MASTER_URI=http://{}:{} && " \
                "simple_navigation_goals_02.exe {} {} {}".format(self.config["master_ip"], port,
                                                                 0.0, 0.0, 180.0)
            escape_p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            try:
                escape_p.wait(self.max_time)
                ok = escape_p.returncode
            except subprocess.TimeoutExpired:
                self.kill(escape_p.pid)
                ok = False

        if not ok:
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals_02 && " \
                "set ROS_MASTER_URI=http://{}:{} && " \
                "simple_navigation_goals_02.exe {} {} {}".format(self.config["master_ip"], port,
                                                                 0.2, 0.0, 180.0)
            escape_p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            try:
                escape_p.wait(self.max_time)
                ok = escape_p.returncode
            except subprocess.TimeoutExpired:
                self.kill(escape_p.pid)
                ok = False

            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals_02 && " \
                "set ROS_MASTER_URI=http://{}:{} && " \
                "simple_navigation_goals_02.exe {} {} {}".format(self.config["master_ip"], port,
                                                                 -0.2, 0.0, 180.0)
            escape_p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            try:
                escape_p.wait(self.max_time)
                ok = escape_p.returncode
            except subprocess.TimeoutExpired:
                self.kill(escape_p.pid)
                ok = False

        if not ok:
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals_02 && " \
                "set ROS_MASTER_URI=http://{}:{} && " \
                "simple_navigation_goals_02.exe {} {} {}".format(self.config["master_ip"], port,
                                                                 0.0, 0.2, 180.0)
            escape_p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            try:
                escape_p.wait(self.max_time)
                ok = escape_p.returncode
            except subprocess.TimeoutExpired:
                self.kill(escape_p.pid)
                ok = False

            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals_02 && " \
                "set ROS_MASTER_URI=http://{}:{} && " \
                "simple_navigation_goals_02.exe {} {} {}".format(self.config["master_ip"], port,
                                                                 0.0, -0.2, 180.0)
            escape_p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            try:
                escape_p.wait(self.max_time)
                ok = escape_p.returncode
            except subprocess.TimeoutExpired:
                self.kill(escape_p.pid)
                ok = False



if __name__ == "__main__":
    config = dict()
    config["initial_index"] = 0
    config["area_range"] = [[0.9, 0.0], [2.0, -2.0]]
    config["angle_range"] = [0.0, 180.0]
    config["spatial_step"] = 0.1
    config["angle_step"] = 20.0

    turtlebot = Turtlebot(config=config)
    # turtlebot.command(0.6, -1.0, 0.0)
    # turtlebot.command(2.1, -2.1, 0.0)
    turtlebot.command(0.0, 0.0, 0.0)

    # done = False
    # while not done:
    #     done, position = turtlebot.step()
    #     print(position)
