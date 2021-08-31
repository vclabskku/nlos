import os 
import numpy as np 
import sounddevice as sd 
from Arduino import Arduino
import time 
#import RealSense

class Echo(): 

    def __init__(self, config):
        self.config = config 

        # Audio interface parameter
        self.device = self.config['device']
        self.samplerate = self.config['samplerate']
        self.bit_depth = self.config['bit_depth']
        self.input_mapping = self.config['input_mapping']
        self.output_mapping = self.config['output_mapping']

        # sine sweep parameter
        self.amplitude = self.config['amplitude']
        self.frequency = self.config['frequency']
        self.transmit_duration = self.config['transmit_duration']
        self.record_duration = self.config['record_duration']
        
        # data path
        self.folder_path = self.config['folder_path']

    # make sine sweep 
    def sine_sweep(self):
        band_width = self.frequency[1] - self.frequency[0]
        n_samples = int(self.transmit_duration * self.samplerate)
        frequency_step = band_width / n_samples
        linear_sweep = np.zeros(shape=(n_samples,), dtype=np.float32)
        frequency = self.frequency[0]
        phase = 0
        for i in range(1, n_samples):
            phase = (phase + 2 * np.pi * frequency / self.samplerate) % (2 * np.pi)
            linear_sweep[i] = self.amplitude * np.sin(phase)
            frequency = frequency + frequency_step 
        
        n_samples = int((self.record_duration - self.transmit_duration) * self.samplerate)
        silence = np.zeros(shape=(n_samples,), dtype=np.float32)
        linear_sweep = np.concatenate((linear_sweep, silence), axis=None)

        return linear_sweep 

    def get_records(self):
        record = sd.playrec(data=self.sine_sweep(),
                            samplerate=self.samplerate,
                            dtype=self.bit_depth,
                            device=self.device,
                            input_mapping=self.input_mapping,
                            output_mapping=self.output_mapping,
                            blocking=True)
        return record

    def file_write(self, record_files):
        current_time = time.strftime('%m%d-%H%M')
        path = self.folder_path + current_time 
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print('Error: Creating directory. ' + path)
        
        np.save(path + '/record_array', record_files) 
        #RealSense.get_images(path)
    
    def get_echos(self):
        record = [] 

        for i in range(9):
            if(i != 8):
                record.append(self.get_records())
                time.sleep(1)
                Arduino.forward()
            else:
                record.append(self.get_records())
                time.sleep(1)
                Arduino.backward() 
                self.file_write(record)

if __name__ == '__main__':
    config = dict() 
    config['device'] = 'UMC1820'
    config['samplerate'] = 48000
    config['bit_depth'] = 'float32'
    config['input_mapping'] = [1, 2, 3, 4, 5, 6, 7, 8]
    config['output_mapping'] = [1, 2]

    config['amplitude'] = 1
    config['frequency'] = [20, 20000]
    config['transmit_duration'] = 0.1
    config['record_duration'] = 0.5 

    config['folder_path'] = 'data/'

    echo = Echo(config=config)
