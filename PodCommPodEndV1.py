import serial
import time
import struct
import threading

FRAME_HEAD_1 = b'\xEB'
FRAME_HEAD_2 = b'\x90'
FRAME_HEAD = FRAME_HEAD_1 + FRAME_HEAD_2

WAITING_FRAME_HEAD_1 = 1
WAITING_FRAME_HEAD_2 = 2
READING_DATA = 3

class MY_SIMU_POD:
    def __init__(self):
        self.state = WAITING_FRAME_HEAD_1
        self.pitch = 0.0
        self.yaw = 0.0

        # /dev/pts/1 on Ubuntu & /dev/ttys003 on MacOS
        self.up_ser = serial.Serial(
            port='/dev/ttys003',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        self.data_buf = bytearray()

    def gen_dow_msg(self):
        return struct.pack('<hh', int(self.pitch * 100), int(self.yaw * 100))
    
    def read_data(self):
        while True:
            data = self.up_ser.read(1)
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
                    if len(data_buf) == 3:
                        print('Up: ', FRAME_HEAD, data_buf)
                        self.state = WAITING_FRAME_HEAD_1
                        time.sleep(1)
                        self.up_ser.write(FRAME_HEAD + b'\x00\x00')

            if self.state == WAITING_FRAME_HEAD_1:
                data_buf = bytearray()
    
    def print_pod(self):
        msg = f'pitch={self.pitch} yaw={self.yaw}'
        l = len(msg)
        col = l + 4
        print('-' * col)
        print('| ' + msg + ' |')
        print('-' * col)
    
    def start_read(self):
        t_read = threading.Thread(target=self.read_data)
        t_read.start()


    def spin(self):
        self.start_read()
        while True:
            self.print_pod()
            time.sleep(1)

pod = MY_SIMU_POD()
pod.spin()