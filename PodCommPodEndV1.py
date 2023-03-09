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

# /dev/pts/3 on Ubuntu & /dev/ttys003 on MacOS
PORT = '/dev/pts/3' if platform == 'linux' else '/dev/ttys003'

def timer(tol=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            # print(f'Time elap: {end_time - start_time:.2f}')
            if end_time - start_time < tol:
                sleep(tol - end_time + start_time)
            # print(f'Ended')
            return result
        return wrapper
    return decorator

class MY_SIMU_POD:
    def __init__(self):
        self.state = WAITING_FRAME_HEAD_1
        self.pitch = 0.0
        self.yaw = 0.0
        self.zoom = 0.0
        self.expected_pitch = 0.0
        self.expected_yaw = 0.0
        self.expected_zoom = 0.0
        self.start_time = time()

        self.up_ser = serial.Serial(
            port=PORT,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        self.data_buf = bytearray()

    def gen_down_msg(self):
        return pack('<hh', int(self.pitch * 100), int(self.yaw * 100))
    
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
                    if len(data_buf) == 4:
                        print('Up buffer: ', FRAME_HEAD, data_buf)
                        up_data = unpack('<hh', data_buf)
                        print('Up data: ', up_data)
                        self.expected_pitch, self.expected_yaw = [data / 100 for data in up_data]
                        self.state = WAITING_FRAME_HEAD_1

            if self.state == WAITING_FRAME_HEAD_1:
                data_buf = bytearray()

    def start_read(self):
        t_read = threading.Thread(target=self.read_data)
        t_read.start()

    @timer(tol=0.5)
    def write_once(self):
        self.up_ser.write(FRAME_HEAD + self.gen_down_msg())

    def write_data(self):
        while True:
            self.write_once()

    def start_write(self):
        t_write = threading.Thread(target=self.write_data)
        t_write.start()
    
    def print_pod(self):
        system('clear')
        print('-' * 40)
        print(f'@ {time() - self.start_time:.2f}')
        print(f'p: {self.pitch:.1f}deg now -> {self.expected_pitch:.1f}deg expected')
        print(f'y: {self.yaw:.1f}deg now -> {self.expected_yaw:.1f}deg expected')
        print('-' * 40)
    
    def adjust(self, val, expected_val):
        tol = 0.1
        diff = expected_val - val
        if abs(diff) < tol:
            return expected_val
        elif diff > tol:
            return val + tol
        elif diff < tol:
            return val - tol

    @timer(tol=1)
    def spin_once(self):
        self.print_pod()
        self.pitch = self.adjust(self.pitch, self.expected_pitch)
        self.yaw = self.adjust(self.yaw, self.expected_yaw)

    def spin(self):
        self.start_read()
        self.start_write()
        while True:
            self.spin_once()


if __name__ == '__main__':
    pod = MY_SIMU_POD()
    pod.spin()