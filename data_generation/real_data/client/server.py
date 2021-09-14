import socket
import time
import threading
import logging
import os
import sys
sys.path.append('C://code')
sys.path.append('C://code/wave')
from radar.radar_signal_processing import radar_activate
from Echo import Echo

NUM_RF_DATA = 5
ROOT_DATA = '//Desktop-3i7mg3m/data'

class Server:

    def __init__(self, host, port, radar, wave, recv_size=1024):
        self.port = port
        self.host = host
        self.radar = radar
        self.wave = wave
        self.recv_size = recv_size
        self.data_root = ROOT_DATA

        print("preparing server")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        print("server start")

    def __del__(self):
        self.sock.close()

    def listen(self):
        while True:
            try:
                self.connectionSock, self.client_addr = self.sock.accept()
                print(f"{str(self.client_addr)} is connected")
            except KeyboardInterrupt:
                self.sock.close()
                break

            t = threading.Thread(target=self.handle_client, args=(self.connectionSock, self.client_addr))
            t.daemon = True
            t.start()

    def handle_client(self, client_socket, addr):

        while True:
            try:
                recvData = client_socket.recv(1024).decode('utf-8')
                logging.info('recieved : {}'.format(recvData))

                command, file_path = recvData.split('-')
                # file_path = "none"
            except:
                logging.error("host connection end")
                return "server connection error"

            try:
                if command == 'rf':
                    self.execute(0, file_path)
                    send_message = 'rf_end'
                elif command == 'wave':
                    self.execute(1, file_path)
                    send_message = 'wave_end'
                # elif command == 'folder':
                #     self.setLogger(file_path)
                #     send_message = 'set folder'
            except:
                logging.error("Error has been occurred")
                send_message = 'error on {}'.format(command)
                logging.error("Unexpected error:", sys.exc_info()[0])
                break

            client_socket.send(send_message.encode('utf-8'))

    def execute(self, flag, file_path):
        file_path = os.path.join(self.data_root, file_path)
        self.check_dir(file_path)
        if flag == 0: ### RF execute
            logging.info("Collect RF data")
            for i in range(NUM_RF_DATA):
                self.radar.get_radar_data_file(radar_data_dir=file_path, num=i)
            logging.info("Collect RF data done")
        elif flag == 1: ### wave execute
            logging.info("Collect Wave data")
            self.wave.get_echos(file_path)
            logging.info("Collect Wave data Done")

        logging.info(f"save data to {file_path}")


    def check_dir(self, path):
        os.makedirs(os.path.join(self.data_root, path), exist_ok=True)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(ROOT_DATA + f"/log/client_computer_{time.strftime('%m%d-%H%M')}.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logging.info(f"LOG DIR SET: {ROOT_DATA}")

    logging.info("initiating RF ... ")
    radar = radar_activate(num_tx_antenna=8,
                           num_rx_antenna=8,
                           radar_info={'radar_lib_path': 'C:/code/radar/Radarlib3_API/Radarlib3.NET.dll',  # fixed
                                       'band': 'low',  # fixed
                                       'sample_delay_to_reference': 27,
                                       'offset_distance_from_reference': 0,
                                       'frame_stitch': 3,
                                       'gain': 4,
                                       'averaging_factor': 1,
                                       'iterations': 30,
                                       'zoom_min': 30,
                                       'zoom_max': 70},
                           switch_info={'switch_lib_path': 'C:/code/radar/Switch_DLL/mcl_SolidStateSwitch64.dll',
                                        # fixed
                                        'tx_switch_serial_number': '11903140023',  # fixed
                                        'rx_switch_serial_number': '11903140017'})  # fixed
    logging.info("Done")

    logging.info("initiating Wave...")
    wave = Echo()
    logging.info("Done")

    host = "192.168.50.174"
    port = 8888
    server = Server(host, port, radar, wave)

    while True:
        try:
            connectionSock, client_addr = server.sock.accept()
            print(f"{str(client_addr)} is connected")

            while True:
                try:
                    recvData = connectionSock.recv(1024).decode('utf-8')
                    logging.info('recieved : {}'.format(recvData))

                    command, file_path = recvData.split('-')
                    # file_path = "none"
                except:
                    logging.error("host connection end")
                    break

                try:
                    if command == 'rf':
                        server.execute(0, file_path)
                        send_message = 'rf_end'
                    elif command == 'wave':
                        server.execute(1, file_path)
                        send_message = 'wave_end'
                    # elif command == 'folder':
                    #     self.setLogger(file_path)
                    #     send_message = 'set folder'
                except:
                    logging.error("Error has been occurred")
                    send_message = 'error on {}'.format(command)
                    logging.error("Unexpected error:", sys.exc_info()[0])
                    break

                connectionSock.send(send_message.encode('utf-8'))
        except KeyboardInterrupt:
            server.sock.close()
            break
