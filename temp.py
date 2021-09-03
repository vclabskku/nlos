# def initialize_roscore(self, turtlebot_num='1'):
#     os.system(self.config["roscore"][turtlebot_num]["terminal_1"]["operation"])
#     self.config["roscore"][turtlebot_num]["terminal_1"]["complete"] = False
#     # if turtlebot_num == 1:
#     #     os.system(self.config["roscore"]["1"]["terminal_1"]["operation"])
#     #     self.config["roscore"]["1"]["terminal_1"]["complete"] = False
#     #
#     # elif turtlebot_num == 2:
#     #     os.system(self.config["roscore"]["2"]["terminal_1"]["operation"])
#     #     self.config["roscore"]["2"]["terminal_1"]["complete"] = False
#     #
#     # else:
#     #     print('plz check turtlebot_number')
#     #     exit()
#
#
# def initialize_turtlebot(self, turtlebot_num='1'):
#     turtlebot = paramiko.SSHClient()
#     turtlebot.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#     turtlebot.connect(self.config["turtlebot_config"][turtlebot_num]["ip"], port='22',
#                       username=self.config["turtlebot_config"][turtlebot_num]["username"],
#                       password=self.config["turtlebot_config"][turtlebot_num]["password"])
#     stdin, stdout, stderr = turtlebot.exec_command(
#         self.config["turtlebot_config"]["1"]["roslanuch"], get_pty=True)
#     self.config["turtlebot_config"]["1"]["complete"] = False
#
#     # if turtlebot_num == 1:
#     #     turtlebot_1 = paramiko.SSHClient()
#     #     turtlebot_1.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#     #     turtlebot_1.connect(self.config["turtlebot_config"]["1"]["ip"], port='22',
#     #                         username=self.config["turtlebot_config"]["1"]["username"],
#     #                         password=self.config["turtlebot_config"]["1"]["password"])
#     #     stdin, stdout, stderr = turtlebot_1.exec_command(
#     #         self.config["turtlebot_config"]["1"]["roslanuch"], get_pty=True)
#     #     self.config["turtlebot_config"]["1"]["complete"] = False
#     #
#     # elif turtlebot_num == 2:
#     #     turtlebot_2 = paramiko.SSHClient()
#     #     turtlebot_2.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#     #     turtlebot_2.connect(self.config["turtlebot_config"]["2"]["ip"], port='22',
#     #                         username=self.config["turtlebot_config"]["2"]["username"],
#     #                         password=self.config["turtlebot_config"]["2"]["password"])
#     #     stdin, stdout, stderr = turtlebot_2.exec_command(
#     #         self.config["turtlebot_config"]["2"]["roslanuch"], get_pty=True)
#     #     self.config["turtlebot_config"]["2"]["complete"] = False
#     #
#     # else:
#     #     print('plz check turtlebot_number')
#     #     exit()
#
#
# def initialize_map(self, turtlebot_num='1'):
#     os.system(self.config["roscore"][turtlebot_num]["terminal_2"]["operation"])
#     self.config["roscore"][turtlebot_num]["terminal_2"]["complete"] = False
#
#     # if turtlebot_num == 1:
#     #     os.system(self.config["roscore"]["1"]["terminal_2"]["operation"])
#     #     self.config["roscore"]["1"]["terminal_2"]["complete"] = False
#     #
#     # elif turtlebot_num == 2:
#     #     os.system(self.config["roscore"]["2"]["terminal_2"]["operation"])
#     #     self.config["roscore"]["2"]["terminal_2"]["complete"] = False
#     #
#     # else:
#     #     print('plz check turtlebot_number')
#     #     exit()
#
#
# def initialize_roscore_set(self):
#     for i in self.config["turtlebot_config"]["using_list"]:
#         print('initialize roscore for turtlebot-' + i)
#         roscore = threading.Thread(target=self.initialize_roscore(), args=(i), daemon=True)
#         roscore.start()
#         time.sleep(30)
#         if not (self.config["roscore"][i]["terminal_1"]["complete"]):
#             print(i + "-th roscore error")
#             exit()
#
#         print('initialize turtlebot-' + i)
#         turtlebot = threading.Thread(target=self.initialize_turtlebot(), args=(i), daemon=True)
#         turtlebot.start()
#         time.sleep(30)
#         if not (self.config["turtlebot_config"][i]["complete"]):
#             print(i + "-th turtlebot error")
#             exit()
#
#         print('initialize map for turtlebot-' + i)
#         map = threading.Thread(target=self.initialize_map(), args=(i), daemon=True)
#         map.start()
#         time.sleep(30)
#         if not (self.config["roscore"][i]["terminal_2"]["complete"]):
#             print(i + "-th roscore error")
#             exit()
#
#

import os
import paramiko

turtlebot = paramiko.SSHClient()
turtlebot.set_missing_host_key_policy(paramiko.AutoAddPolicy)
turtlebot.connect('192.168.50.116', port='22', username='turtlebot-01', password='vclab201703')
print('connect')
stdin, stdout, stderr = turtlebot.exec_command('roslaunch turtlebot3_bringup turtlebot3_robot.launch', get_pty=True)
print(stdout.read())
