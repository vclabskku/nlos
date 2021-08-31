from Echo import Echo
from Arduino import Arduino
import time 

class Collector():

    def __init__(self, config):

        self.config = config
        self.arduino = Arduino(self.config['arduino_config'])
        self.echo = Echo(self.config["echo_config"])
    
    '''
    이 부분 main에 추가 필요
    '''
    def collect(self):
        record = []
        '''
        원점으로 보내기
        '''
        self.arduino.initialize()
        for i in range(9):
            if(i != 8):
                record.append(self.echo.get_records())
                self.arduino.forward()
                time.sleep(0.5)
            else:
                record.append(self.echo.get_records())
                self.arduino.backward() 
                self.echo.file_write(record)
        