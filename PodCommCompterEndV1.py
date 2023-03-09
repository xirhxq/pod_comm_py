import serial
import threading
from time import time, sleep
from struct import pack, unpack
from sys import platform
from os import system


FRAME_HEAD_1 = b'\xEB'
FRAME_HEAD_2 = b'\x90'
FRAME_HEAD = FRAME_HEAD_1 + FRAME_HEAD_2

WAITING_FRAME_HEAD_1 = 1
WAITING_FRAME_HEAD_2 = 2
READING_DATA = 3

# /dev/pts/2 on Ubuntu & /dev/ttys002 on MacOS
# using socat to generate fake serial ports `socat -d -d pty pty`
PORT = '/dev/pts/2' if platform == 'linux' else ('COM2' if platform == 'win32' else '/dev/ttys002')


class POD_COMM:
    def __init__(self):
        self.state = WAITING_FRAME_HEAD_1
        self.expected_pitch = 0.0
        self.expected_yaw = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.start_time = time()

        self.down_ser = serial.Serial(
            port=PORT,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        self.data_buf = bytearray()
    
    def gen_up_msg(self):
        return pack('<hh', int(self.expected_pitch * 100), int(self.expected_yaw * 100))

    def read_data(self):
        while True:
            data = self.down_ser.read(1)

            if data:
                if self.state == WAITING_FRAME_HEAD_1:
                    if data == FRAME_HEAD_1:
                        self.state = WAITING_FRAME_HEAD_2
                elif self.state == WAITING_FRAME_HEAD_2:
                    if data == FRAME_HEAD_2:
                        self.state = READING_DATA
                        data_buf = bytearray()
                elif self.state == READING_DATA:
                    data_buf.append(data[0])
                    if len(data_buf) == 21:
                        print('Down buffer: ', FRAME_HEAD, data_buf)
                        sleep(1)
                        # down_data = unpack('<hh', data_buf)
                        # print('Down data: ', down_data)
                        # self.pitch, self.yaw = [data / 100 for data in down_data]
                        self.state = WAITING_FRAME_HEAD_1

            if self.state == WAITING_FRAME_HEAD_1:
                data_buf = bytearray()
    
    def start_read(self):
        t_read = threading.Thread(target=self.read_data)
        t_read.start()

    def write_data(self):
        while True:
            self.down_ser.write(FRAME_HEAD + self.gen_up_msg())
            sleep(1)
            
    def start_write(self):
        t_write = threading.Thread(target=self.write_data)
        t_write.start()


    def spin(self):
        self.start_read()
        # self.start_write()
        while True:
            pass
            # self.expected_pitch, self.expected_yaw = list(map(float, input('Input expected pitch and yaw:').split()))


if __name__ == '__main__':
    pod_comm = POD_COMM()
    pod_comm.spin()