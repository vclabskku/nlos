import serial
import time  

class Arduino():

    def __init__(self, config):
        self.config = config
        self.port = self.config['port']
        self.baudrate = self.config['baudrate']
        self.serial = serial.Serial(self.port, self.baudrate)

    def initialize(self):
        self.serial.flush() 
        arduino_to_python = ''
        while True:
            if(self.serial.in_waiting > 0):
                arduino_to_python = self.serial.readline().decode('utf-8').strip()
            if (arduino_to_python == '3'):
                break 
            time.sleep(1)
        

    def forward(self):
        python_to_arduino = ''
        arduino_to_python = ''

        if (self.serial.readable()):
            python_to_arduino = '1'
            python_to_arduino = python_to_arduino.encode('utf-8')
            self.serial.write(python_to_arduino)
            self.serial.flush() 


        while True:
            self.serial.flush() 
            if(self.serial.in_waiting > 0):
                arduino_to_python = self.serial.readline().decode('utf-8').strip()
            if (arduino_to_python == '3'):
                break

    def backward(self):
        python_to_arduino = ''
        arduino_to_python = ''
        
        if (self.serial.readable()):
            python_to_arduino = '2'
            python_to_arduino = python_to_arduino.encode('utf-8')
            self.serial.write(python_to_arduino)
            self.serial.flush() 

        while True:
            self.serial.flush()
            if(self.serial.in_waiting > 0):
                arduino_to_python = self.serial.readline().decode('utf-8').strip()
            if (arduino_to_python == '3'):
                break

    
if __name__ == '__main__':
    config = dict()
    config['port'] = '/dev/cu/usbmodem146201'
    config['baudrate'] = 9600

    arduino = Arduino(config)
