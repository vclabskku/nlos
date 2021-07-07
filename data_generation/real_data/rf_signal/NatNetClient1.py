# Copyright © 2018 Naturalpoint
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# OptiTrack NatNet direct depacketization library for Python 3.x

import socket
import struct
from typing import Dict, List, Optional
from threading import Thread
import csv
import datetime
import numpy as np
from data_generation.real_data.rf_signal.mimo_radar_system import MimoRadarSystem


def trace(*args):
    pass  # print( "".join(map(str,args)) )


# Create structs for reading various object types to speed up parsing.
Vector3 = struct.Struct('<fff')
Quaternion = struct.Struct('<ffff')
FloatValue = struct.Struct('<f')
DoubleValue = struct.Struct('<d')


class NatNetClient:
    def __init__(self):
        # Change this value to the IP address of the NatNet server.
        self.serverIPAddress = "127.0.0.1"

        # Change this value to the IP address of your local network interface
        self.localIPAddress = "127.0.0.1"

        # This should match the multicast address listed in Motive's streaming settings.
        self.multicastAddress = "239.255.42.99"

        # NatNet Command channel
        self.commandPort = 1510

        # NatNet Data channel
        self.dataPort = 1511

        # Set this to a callback method of your choice to receive per-rigid-body data at each frame.
        self.rigidBodyListener = None

        # NatNet stream version. This will be updated to the actual version the server is using during initialization.
        self.__natNetStreamVersion = (3, 1, 0, 0)

        self.rigidbody = []

        self._cnt = int(input("What next? : "))
        self._nowDate = None


    # Client/server message ids
    NAT_PING = 0
    NAT_PINGRESPONSE = 1
    NAT_REQUEST = 2
    NAT_RESPONSE = 3
    NAT_REQUEST_MODELDEF = 4
    NAT_MODELDEF = 5
    NAT_REQUEST_FRAMEOFDATA = 6
    NAT_FRAMEOFDATA = 7
    NAT_MESSAGESTRING = 8
    NAT_DISCONNECT = 9
    NAT_UNRECOGNIZED_REQUEST = 100

    # Create a data socket to attach to the NatNet stream

    def set_radar_system(self, num_tx_antenna: int, num_rx_antenna: int, radar_info: Dict, switch_info: Dict,
                         pulse_dir: str, snr_for_wiener_dB: int, tx_antenna_position: np.ndarray,
                         rx_antenna_position: np.ndarray, volume_min_point: np.ndarray, volume_max_point: np.ndarray,
                         volume_num_step: np.ndarray, camera):
        self.num_tx_antenna = num_tx_antenna
        self.num_rx_antenna = num_rx_antenna
        self.radar_info = radar_info
        self.switch_info = switch_info
        self.dir_pulse = pulse_dir
        self.snr_for_wiener_dB = snr_for_wiener_dB
        self.tx_antenna_position = tx_antenna_position
        self.rx_antenna_position = rx_antenna_position
        self.volume_min_point = volume_min_point
        self.volume_max_point = volume_max_point
        self.volume_num_step = volume_num_step
        self.radar_system = MimoRadarSystem(num_tx_antenna=self.num_tx_antenna, num_rx_antenna=self.num_rx_antenna,
                                            radar_info=self.radar_info, switch_info=self.switch_info, is_mimo=True,
                                            h_t_mode='none', snr_for_wiener_dB=self.snr_for_wiener_dB)
        # self.radar_system.set_entire_matched_filter_input_dir(self.dir_pulse)
        self.camera = camera

    def radar_data(self, flag):
        # self.camera = camera
        while flag == 1:
            radar_signal = self.radar_system.get_all_radar_signal()

            print(radar_signal.shape)
            print(radar_signal[0][0][:])
            self._nowDate = datetime.datetime.now()
            with open('____RADAR/%s.csv' % (str(self._cnt).zfill(8)), 'a',
                      newline='') as f:
                writer = csv.writer(f)
                for i in range(self.num_tx_antenna):
                    for j in range(self.num_rx_antenna):
                        writer.writerow(radar_signal[i][j].real)
            self.camera.save_img()
            flag = 0

    def __createDataSocket(self, port):
        result = socket.socket(socket.AF_INET,  # Internet
                               socket.SOCK_DGRAM,
                               socket.IPPROTO_UDP)  # UDP

        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                          socket.inet_aton(self.multicastAddress) + socket.inet_aton(self.localIPAddress))

        result.bind((self.localIPAddress, port))

        return result

    # Create a command socket to attach to the NatNet stream
    def __createCommandSocket(self):
        result = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result.bind(('', 0))
        result.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        return result

    # Unpack a rigid body object from a data packet
    def __unpackRigidBody(self, data):
        offset = 0

        # ID (4 bytes)
        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("ID:", id)

        # Position and orientation
        pos = Vector3.unpack(data[offset:offset + 12])
        offset += 12
        trace("\tPosition:", pos[0], ",", pos[1], ",", pos[2])
        rot = Quaternion.unpack(data[offset:offset + 16])
        offset += 16
        trace("\tOrientation:", rot[0], ",", rot[1], ",", rot[2], ",", rot[3])

        # Send information to any listener.
        # if self.rigidBodyListener is not None:
        #     self.rigidBodyListener(id, pos, rot)

        self._nowDate = datetime.datetime.now()
        self.rigidbody = np.array([pos[0], pos[1], pos[2], rot[0], rot[1], rot[2]])
        # print('_cnt is : ', self._cnt)


        # RB Marker Data ( Before version 3.0.  After Version 3.0 Marker data is in description )
        if (self.__natNetStreamVersion[0] < 3 and self.__natNetStreamVersion[0] != 0):
            # Marker count (4 bytes)
            markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            markerCountRange = range(0, markerCount)
            trace("\tMarker Count:", markerCount)

            # Marker positions
            for i in markerCountRange:
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                trace("\tMarker", i, ":", pos[0], ",", pos[1], ",", pos[2])

            if (self.__natNetStreamVersion[0] >= 2):
                # Marker ID's
                for i in markerCountRange:
                    id = int.from_bytes(data[offset:offset + 4], byteorder='little')
                    offset += 4
                    trace("\tMarker ID", i, ":", id)

                # Marker sizes
                for i in markerCountRange:
                    size = FloatValue.unpack(data[offset:offset + 4])
                    offset += 4
                    trace("\tMarker Size", i, ":", size[0])

        if (self.__natNetStreamVersion[0] >= 2):
            markerError, = FloatValue.unpack(data[offset:offset + 4])
            offset += 4
            trace("\tMarker Error:", markerError)

        # Version 2.6 and later
        if (((self.__natNetStreamVersion[0] == 2) and (self.__natNetStreamVersion[1] >= 6)) or
                self.__natNetStreamVersion[0] > 2 or self.__natNetStreamVersion[0] == 0):
            param, = struct.unpack('h', data[offset:offset + 2])
            trackingValid = (param & 0x01) != 0
            offset += 2
            trace("\tTracking Valid:", 'True' if trackingValid else 'False')

        return offset

    # Unpack a skeleton object from a data packet
    def __unpackSkeleton(self, data):
        offset = 0

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("ID:", id)

        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Rigid Body Count:", rigidBodyCount)
        for j in range(0, rigidBodyCount):
            offset += self.__unpackRigidBody(data[offset:])

        return offset

        # Unpack data from a motion capture frame message

    def __unpackMocapData(self, data):
        trace("Begin MoCap Frame\n-----------------\n")

        data = memoryview(data)
        offset = 0

        # Frame number (4 bytes)
        frameNumber = int.from_bytes(data[offset:offset + 4], byteorder='little')

        offset += 4
        trace("Frame #:", frameNumber)

        # Marker set count (4 bytes)
        markerSetCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Marker Set Count:", markerSetCount)

        for i in range(0, markerSetCount):
            # Model name
            modelName, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(modelName) + 1
            trace("Model Name:", modelName.decode('utf-8'))

            # Marker count (4 bytes)
            markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Marker Count:", markerCount)

            for j in range(0, markerCount):
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                # trace( "\tMarker", j, ":", pos[0],",", pos[1],",", pos[2] )

        # Unlabeled markers count (4 bytes)
        unlabeledMarkersCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Unlabeled Markers Count:", unlabeledMarkersCount)

        list_distance = []
        list_position = []

        for i in range(0, unlabeledMarkersCount):
            pos = Vector3.unpack(data[offset:offset + 12])
            offset += 12
            trace("\tMarker", i, ":", pos[0], ",", pos[1], ",", pos[2])
            # if self.unlabeledListener is not None:
            #     self.unlabeledListener(pos)
            # with open('____MOTIVE/%s.csv' % (str(self._cnt).zfill(8)), 'a',
            #           newline='') as f:
            #     writer = csv.writer(f)
            #     writer.writerow(np.array([pos[0], pos[1], pos[2]]))
            # list_position.append(np.array([pos[0], pos[1], pos[2]]))

        # Rigid body count (4 bytes)
        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Rigid Body Count:", rigidBodyCount)

        for i in range(0, rigidBodyCount):
            offset += self.__unpackRigidBody(data[offset:])

        self.radar_data(flag=1)



        # Version 2.1 and later
        skeletonCount = 0
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] > 0) or self.__natNetStreamVersion[
            0] > 2):
            skeletonCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Skeleton Count:", skeletonCount)
            for i in range(0, skeletonCount):
                offset += self.__unpackSkeleton(data[offset:])

        # Labeled markers (Version 2.3 and later)
        labeledMarkerCount = 0
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] > 3) or self.__natNetStreamVersion[
            0] > 2):
            labeledMarkerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Labeled Marker Count:", labeledMarkerCount)

            for i in range(0, labeledMarkerCount):
                id = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                size = FloatValue.unpack(data[offset:offset + 4])
                offset += 4
                # if self.labeledListener is not None:
                #     self.labeledListener(pos)
                with open('____MOTIVE/%s.csv' % (str(self._cnt).zfill(8)), 'a',
                          newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(pos)

                # Version 2.6 and later
                if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 6) or
                        self.__natNetStreamVersion[0] > 2 or major == 0):
                    param, = struct.unpack('h', data[offset:offset + 2])
                    offset += 2
                    occluded = (param & 0x01) != 0
                    pointCloudSolved = (param & 0x02) != 0
                    modelSolved = (param & 0x04) != 0

                # Version 3.0 and later
                if ((self.__natNetStreamVersion[0] >= 3) or major == 0):
                    residual, = FloatValue.unpack(data[offset:offset + 4])
                    offset += 4
                    trace("Residual:", residual)

        self._cnt += 1

        # Force Plate data (version 2.9 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 9) or self.__natNetStreamVersion[
            0] > 2):
            forcePlateCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Force Plate Count:", forcePlateCount)
            for i in range(0, forcePlateCount):
                # ID
                forcePlateID = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                trace("Force Plate", i, ":", forcePlateID)

                # Channel Count
                forcePlateChannelCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4

                # Channel Data
                for j in range(0, forcePlateChannelCount):
                    trace("\tChannel", j, ":", forcePlateID)
                    forcePlateChannelFrameCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                    offset += 4
                    for k in range(0, forcePlateChannelFrameCount):
                        forcePlateChannelVal = int.from_bytes(data[offset:offset + 4], byteorder='little')
                        offset += 4
                        trace("\t\t", forcePlateChannelVal)

        # Device data (version 2.11 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 11) or self.__natNetStreamVersion[
            0] > 2):
            deviceCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Device Count:", deviceCount)
            for i in range(0, deviceCount):
                # ID
                deviceID = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                trace("Device", i, ":", deviceID)

                # Channel Count
                deviceChannelCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4

                # Channel Data
                for j in range(0, deviceChannelCount):
                    trace("\tChannel", j, ":", deviceID)
                    deviceChannelFrameCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                    offset += 4
                    for k in range(0, deviceChannelFrameCount):
                        deviceChannelVal = int.from_bytes(data[offset:offset + 4], byteorder='little')
                        offset += 4
                        trace("\t\t", deviceChannelVal)

        # Timecode
        timecode = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        timecodeSub = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        # Timestamp (increased to double precision in 2.7 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 7) or self.__natNetStreamVersion[
            0] > 2):
            timestamp, = DoubleValue.unpack(data[offset:offset + 8])
            offset += 8
        else:
            timestamp, = FloatValue.unpack(data[offset:offset + 4])
            offset += 4

        # Hires Timestamp (Version 3.0 and later)
        if ((self.__natNetStreamVersion[0] >= 3) or major == 0):
            stampCameraExposure = int.from_bytes(data[offset:offset + 8], byteorder='little')
            offset += 8
            stampDataReceived = int.from_bytes(data[offset:offset + 8], byteorder='little')
            offset += 8
            stampTransmit = int.from_bytes(data[offset:offset + 8], byteorder='little')
            offset += 8

        # Frame parameters
        param, = struct.unpack('h', data[offset:offset + 2])
        isRecording = (param & 0x01) != 0
        trackedModelsChanged = (param & 0x02) != 0
        offset += 2

        # Send information to any listener.
        # if self.newFrameListener is not None:
        #     self.newFrameListener(frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
        #                           labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording,
        #                           trackedModelsChanged)

    # Unpack a marker set description packet
    def __unpackMarkerSetDescription(self, data):
        offset = 0

        name, separator, remainder = bytes(data[offset:]).partition(b'\0')
        offset += len(name) + 1
        trace("Markerset Name:", name.decode('utf-8'))

        markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, markerCount):
            name, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(name) + 1
            trace("\tMarker Name:", name.decode('utf-8'))

        return offset

    # Unpack a rigid body description packet
    def __unpackRigidBodyDescription(self, data):
        offset = 0

        # Version 2.0 or higher
        if (self.__natNetStreamVersion[0] >= 2):
            name, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(name) + 1
            trace("\tRigidBody Name:", name.decode('utf-8'))

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        parentID = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        timestamp = Vector3.unpack(data[offset:offset + 12])
        offset += 12

        # Version 3.0 and higher, rigid body marker information contained in description
        if (self.__natNetStreamVersion[0] >= 3 or self.__natNetStreamVersion[0] == 0):
            markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("\tRigidBody Marker Count:", markerCount)

            markerCountRange = range(0, markerCount)
            for marker in markerCountRange:
                markerOffset = Vector3.unpack(data[offset:offset + 12])
                offset += 12
            for marker in markerCountRange:
                activeLabel = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4

        return offset

    # Unpack a skeleton description packet
    def __unpackSkeletonDescription(self, data):
        offset = 0

        name, separator, remainder = bytes(data[offset:]).partition(b'\0')
        offset += len(name) + 1
        trace("\tMarker Name:", name.decode('utf-8'))

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, rigidBodyCount):
            offset += self.__unpackRigidBodyDescription(data[offset:])

        return offset

    # Unpack a data description packet
    def __unpackDataDescriptions(self, data):
        offset = 0
        datasetCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, datasetCount):
            type = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            if (type == 0):
                offset += self.__unpackMarkerSetDescription(data[offset:])
            elif (type == 1):
                offset += self.__unpackRigidBodyDescription(data[offset:])
            elif (type == 2):
                offset += self.__unpackSkeletonDescription(data[offset:])

    def __dataThreadFunction(self, socket):
        while True:
            # Block for input

            data, addr = socket.recvfrom(32768)  # 32k byte buffer size
            if (len(data) > 0):
                self.__processMessage(data)


    def __dataThreadFunction_only_one(self, socket, isCommand=False):
        data, addr = socket.recvfrom(32768)  # 32k byte buffer size
        # if isCommand:
        #     print(data)

        if len(data) > 0:
            self.__processMessage(data)


    def __processMessage(self, data):
        trace("Begin Packet\n------------\n")

        messageID = int.from_bytes(data[0:2], byteorder='little')
        trace("Message ID:", messageID)

        packetSize = int.from_bytes(data[2:4], byteorder='little')
        trace("Packet Size:", packetSize)

        offset = 4
        if (messageID == self.NAT_FRAMEOFDATA):
            self.__unpackMocapData(data[offset:])
            # return self.__unpackMocapData(data[offset:])
        elif (messageID == self.NAT_MODELDEF):
            self.__unpackDataDescriptions(data[offset:])
        elif (messageID == self.NAT_PINGRESPONSE):
            offset += 256  # Skip the sending app's Name field
            offset += 4  # Skip the sending app's Version info
            self.__natNetStreamVersion = struct.unpack('BBBB', data[offset:offset + 4])
            offset += 4
        elif (messageID == self.NAT_RESPONSE):
            if (packetSize == 4):
                commandResponse = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
            else:
                message, separator, remainder = bytes(data[offset:]).partition(b'\0')
                offset += len(message) + 1
                trace("Command response:", message.decode('utf-8'))
        elif (messageID == self.NAT_UNRECOGNIZED_REQUEST):
            trace("Received 'Unrecognized request' from server")
        elif (messageID == self.NAT_MESSAGESTRING):
            message, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(message) + 1
            trace("Received message from server:", message.decode('utf-8'))
        else:
            trace("ERROR: Unrecognized packet type")

        trace("End Packet\n----------\n")

        return None

    def sendCommand(self, command, commandStr, socket, address):
        # Compose the message in our known message format
        if (command == self.NAT_REQUEST_MODELDEF or command == self.NAT_REQUEST_FRAMEOFDATA):
            packetSize = 0
            commandStr = ""
        elif (command == self.NAT_REQUEST):
            packetSize = len(commandStr) + 1
        elif (command == self.NAT_PING):
            commandStr = "Ping"
            packetSize = len(commandStr) + 1

        data = command.to_bytes(2, byteorder='little')
        data += packetSize.to_bytes(2, byteorder='little')

        data += commandStr.encode('utf-8')
        data += b'\0'

        socket.sendto(data, address)

    def run(self):
        # Create the data socket
        self.dataSocket = self.__createDataSocket(self.dataPort)
        if (self.dataSocket is None):
            print("Could not open data channel")
            exit

        # Create the command socket
        self.commandSocket = self.__createCommandSocket()
        if (self.commandSocket is None):
            print("Could not open command channel")
            exit

        # Create a separate thread for receiving data packets
        dataThread = Thread(target=self.__dataThreadFunction, args=(self.dataSocket,))
        dataThread.start()

        # Create a separate thread for receiving command packets
        commandThread = Thread(target=self.__dataThreadFunction, args=(self.commandSocket,))
        commandThread.start()
        self.sendCommand(self.NAT_REQUEST_MODELDEF, "", self.commandSocket, (self.serverIPAddress, self.commandPort))


    def run_onetime(self):
        # Create the data socket
        self.dataSocket = self.__createDataSocket(self.dataPort)
        if self.dataSocket is None:
            print("Could not open data channel")
            exit

        # Create the command socket
        self.commandSocket = self.__createCommandSocket()
        if self.commandSocket is None:
            print("Could not open command channel")
            exit

        # Create a separate thread for receiving data packets
        # dataThread = Thread(target=self.__dataThreadFunction_only_one, args=(self.dataSocket,))
        # dataThread.start()

        self.__dataThreadFunction_only_one(self.dataSocket)

        # Create a separate thread for receiving command packets
        # 쓰레드로 넣지 않으면 작동하지 않는다.
        commandThread = Thread(target=self.__dataThreadFunction_only_one, args=(self.commandSocket, True))
        commandThread.start()

        self.sendCommand(self.NAT_REQUEST_MODELDEF, "", self.commandSocket, (self.serverIPAddress, self.commandPort))
