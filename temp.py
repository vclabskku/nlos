import os
import time
import paramiko
import threading
import _thread
from multiprocessing import Process, Manager
from subprocess import Popen, PIPE
import time

def get_config():
    config = dict()
    config["turtlebot_config"] = dict()
    config["turtlebot_config"]["using_list"] = ['1', '2']
    config["turtlebot_config"]["1"] = dict()
    config["turtlebot_config"]["2"] = dict()
    config["turtlebot_config"]["1"]["ip"] = '192.168.50.116'
    config["turtlebot_config"]["1"]["username"] = 'turtlebot-01'
    config["turtlebot_config"]["1"]["password"] = 'vclab201703'
    config["turtlebot_config"]["1"]["roslanuch"] = 'roslaunch turtlebot3_bringup turtlebot3_robot.launch'
    config["turtlebot_config"]["2"]["ip"] = '192.168.50.55'
    config["turtlebot_config"]["2"]["username"] = 'ubuntu'
    config["turtlebot_config"]["2"]["password"] = 'vclab201703'
    config["turtlebot_config"]["2"]["roslanuch"] = 'roslaunch turtlebot3_bringup turtlebot3_robot.launch'

    config["roscore"] = dict()
    config["roscore"]["1"] = dict()
    config["roscore"]["2"] = dict()
    config["roscore"]["1"]["terminal_1"] = dict()
    config["roscore"]["1"]["terminal_2"] = dict()
    config["roscore"]["2"]["terminal_1"] = dict()
    config["roscore"]["2"]["terminal_2"] = dict()
    config["roscore"]["1"]["terminal_1"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                        "c://opt//ros//melodic//x64//setup.bat && " \
                                                        "c://ws//turtlebot3//devel//setup.bat && " \
                                                        "roscore --port 11311"
    config["roscore"]["1"]["terminal_2"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                        "c://opt//ros//melodic//x64//setup.bat && " \
                                                        "c://ws//turtlebot3//devel//setup.bat && " \
                                                        "set ROS_MASTER_URI=http://192.168.50.192:11311/ && " \
                                                        "roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c://ws//maps//map_01.yaml"
    config["roscore"]["2"]["terminal_1"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                        "c://opt//ros//melodic//x64//setup.bat && " \
                                                        "c://ws//turtlebot3//devel//setup.bat && " \
                                                        "roscore --port 11312"
    config["roscore"]["2"]["terminal_2"]["operation"] = "set ChocolateyInstall=c://opt//chocolatey && " \
                                                        "c://opt//ros//melodic//x64//setup.bat && " \
                                                        "c://ws//turtlebot3//devel//setup.bat && " \
                                                        "set ROS_MASTER_URI=http://192.168.50.192:11312/ && " \
                                                        "roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c://ws//maps//map_02.yaml"
    return config

class Collector():

    def __init__(self, config):
        self.config = config

    def initialize_roscore(self, turtlebot_num='1'):
        threading.Thread(target=os.system,
                         args=(self.config["roscore"][turtlebot_num]["terminal_1"]["operation"],),
                         daemon=True)
        # _thread.start_new_thread(os.system,
        #                          (self.config["roscore"][turtlebot_num]["terminal_1"]["operation"],))

    def initialize_turtlebot(self, turtlebot_num='1'):
        retries = 10
        turtlebot = paramiko.SSHClient()
        turtlebot.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        for x in range(retries):
            try:
                turtlebot.connect(self.config["turtlebot_config"][turtlebot_num]["ip"], port='22',
                                  username=self.config["turtlebot_config"][turtlebot_num]["username"],
                                  password=self.config["turtlebot_config"][turtlebot_num]["password"],
                                  timeout=5)
                break
            except:
                pass
        for x in range(retries):
            stdin, stdout, stderr = turtlebot.exec_command(
                self.config["turtlebot_config"]["1"]["roslanuch"], get_pty=True)
        # stdin, stdout, stderr = turtlebot.exec_command(
        #     self.config["turtlebot_config"]["1"]["roslanuch"], get_pty=True)

    def initialize_map(self, turtlebot_num='1'):
        _thread.start_new_thread(os.system,
                                 (self.config["roscore"][turtlebot_num]["terminal_2"]["operation"],))

    def initialize_roscore_set(self):
        for i in self.config["turtlebot_config"]["using_list"]:
            process_roscore = Process(target=self.initialize_roscore, args=(i,))



            print('initialize roscore for turtlebot-'+i)
            threading.Thread(target=os.system,
                             args=(self.config["roscore"][i]["terminal_1"]["operation"],),
                             daemon=True)
            time.sleep(30)

            # print('\ninitialize turtlebot-'+i)
            # turtlebot = threading.Thread(target=self.initialize_turtlebot(), args=(i), daemon=True)
            # turtlebot.start()
            # time.sleep(30)
            #
            # print('\ninitialize map for turtlebot-'+i)
            # _thread.start_new_thread(os.system,
            #                          (self.config["roscore"][i]["terminal_2"]["operation"],))
            # time.sleep(30)

def execute(command):
    process = Popen(command, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            continue
        yield line

def initialize_roscore(config, turtlebot_num, manager):
    for path in execute(config["roscore"][turtlebot_num]["terminal_1"]["operation"]):
        print(path.decode('utf-8'))
        if "started core service [/rosout]" in path.decode('utf-8'):
            manager[0] = True

def initialize_turtlebot(config, turtlebot_num, manager):
    retries = 10
    turtlebot = paramiko.SSHClient()
    turtlebot.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    for x in range(retries):
        try:
            turtlebot.connect(config["turtlebot_config"][turtlebot_num]["ip"], port='22',
                              username=config["turtlebot_config"][turtlebot_num]["username"],
                              password=config["turtlebot_config"][turtlebot_num]["password"],
                              timeout=5)
            break
        except:
            pass

    for x in range(retries):
        try:
            stdin, stdout, stderr = turtlebot.exec_command(
                config["turtlebot_config"][turtlebot_num]["roslanuch"], get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line, end="")
                if 'Calibration End' in line:
                    manager[1] = True
            break
        except:
            pass

def initialize_map(config, turtlebot_num, manager):
    for path in execute(config["roscore"][turtlebot_num]["terminal_2"]["operation"]):
        print(path.decode('utf-8'))
        if "process[rviz-5]: started with pid" in path.decode('utf-8'):
            manager[2] = True

if __name__ == '__main__':
    config = get_config()
    manager = Manager().list([False, False, False])

    process_list = []
    process_list.append(Process(target=initialize_roscore, args=(config, '2', manager)))
    process_list.append(Process(target=initialize_turtlebot, args=(config, '2', manager)))
    process_list.append(Process(target=initialize_map, args=(config, '2', manager)))

    process_list[0].start()
    while(True):
        if manager[0] == True:
            break
    process_list[1].start()
    while(True):
        if manager[1] == True:
            break
    process_list[2].start()
    while(True):
        if manager[2] == True:
            break

    time.sleep(100)
    process_list[0].join()
    process_list[1].join()
    process_list[2].join()