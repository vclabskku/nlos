import paramiko
import time
import subprocess

'''
SSH 접속
'''
def waitStrems(chan):
    time.sleep(1)
    outdata=errdata = ""

    while chan.recv_ready():
        outdata += chan.recv(1000).decode()
    while chan.recv_stderr_ready():
        errdata += chan.recv_stderr(1000).decode()

    return outdata, errdata

# turtlebot_1 = paramiko.SSHClient()
# turtlebot_1.set_missing_host_key_policy(paramiko.AutoAddPolicy)
# turtlebot_1.connect('192.168.50.124', port='22', username='turtlebot-01', password='vclab201703')
# print('Connection End')
#
# stdin, stdout, stderr = turtlebot_1.exec_command("roslaunch turtlebot3_bringup turtlebot3_robot.launch\n", get_pty=True)
# print(stdout.readlines())

turtlebot_2 = paramiko.SSHClient()
turtlebot_2.set_missing_host_key_policy(paramiko.AutoAddPolicy)
turtlebot_2.connect('192.168.50.55', port='22', username='ubuntu', password='vclab201703')
print('Connection End')

stdin, stdout, stderr = turtlebot_2.exec_command("roslaunch turtlebot3_bringup turtlebot3_robot.launch\n", get_pty=True)
print(stdout.readlines())









# '''
# 여기에 실패시 조건문이랑 성공시 조건문 추가
# '''
#
# '''
# 연결 종료
# '''
# turtlebot_1.close()
# turtlebot_2.close()

'''
powershell & roscore
'''

import os
import subprocess

command_roscore = "set ChocolateyInstall=c://opt//chocolatey && c://opt//ros//melodic//x64//setup.bat && c://ws//turtlebot3//devel//setup.bat && roscore --port 11311"
command_turtlebot = "roslaunch turtlebot3_bringup turtlebot3_robot.launch"
command_map = "set ChocolateyInstall=c://opt//chocolatey && c://opt//ros//melodic//x64//setup.bat && c://ws//turtlebot3//devel//setup.bat && roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=c:\ws\maps\map_01.yaml"
# os.system(command_map)
