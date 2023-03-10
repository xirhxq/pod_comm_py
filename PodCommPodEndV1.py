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
PORT = '/dev/pts/3' if platform == 'linux' else ('COM2' if platform == 'win32' else '/dev/ttys003')

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
        msg = pack('<BBBhIhhhBhh', 0, 0, 0, int(self.zoom * 100), 0, int(self.pitch * 100), int(self.yaw * 100), 0, 0, 0, 0)
        check_sum = sum(msg)
        return msg + pack('<B', check_sum & 0xff)
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
                    if len(data_buf) == 30:
                        # print('Up buffer: ', FRAME_HEAD, data_buf)
                        up_data = unpack('<xBhh' + 'x' * 10 + 'B' + 'x' * 11 + 'H', data_buf)
                        # print('Up data: ', up_data)
                        order = up_data[0]
                        pitch_val = up_data[1] / 100
                        yaw_val = up_data[2] / 100
                        laser_setting = up_data[3]
                        check_sum = up_data[4]
                        if check_sum != sum(data_buf[:-2]):
                            assert 0
                        elif check_sum > 0:
                            pass
                            print(data_buf.hex())
                            # print(f'Check sum right: {check_sum}')

                        if order == 0x1D:
                            self.yaw -= 0.01
                        elif order == 0x1F:
                            self.yaw += 0.01
                        elif order == 0x21:
                            self.pitch -= 0.01
                        elif order == 0x23:
                            self.pitch += 0.01

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
        print('\x1b[H')
        print('-' * 40)
        print(f'@ {time() - self.start_time:.2f}')
        print(f'p: {self.pitch:.2f}deg now -> {self.expected_pitch:.1f}deg expected')
        print(f'y: {self.yaw:.2f}deg now -> {self.expected_yaw:.1f}deg expected')
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

    @timer(tol=0.04)
    def spin_once(self):
        self.print_pod()
        # self.pitch = self.adjust(self.pitch, self.expected_pitch)
        # self.yaw = self.adjust(self.yaw, self.expected_yaw)
        pass

    def spin(self):
        self.start_read()
        self.start_write()
        while True:
            try:
                self.spin_once()
            except KeyboardInterrupt:
                exit()


if __name__ == '__main__':
    pod = MY_SIMU_POD()
    pod.spin()