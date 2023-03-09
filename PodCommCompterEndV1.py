import serial
import time
import struct

FRAME_HEAD_1 = b'\xEB'
FRAME_HEAD_2 = b'\x90'
FRAME_HEAD = FRAME_HEAD_1 + FRAME_HEAD_2

WAITING_FRAME_HEAD_1 = 1
WAITING_FRAME_HEAD_2 = 2
READING_DATA = 3

# /dev/pts/2 on Ubuntu & /dev/ttys002 on MacOS
down_ser = serial.Serial(
    port='/dev/ttys002',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.5
)

state = WAITING_FRAME_HEAD_1

data_buf = bytearray()

while True:
    data = down_ser.read(1)

    if data:
        if state == WAITING_FRAME_HEAD_1:
            if data == FRAME_HEAD_1:
                state = WAITING_FRAME_HEAD_2
        elif state == WAITING_FRAME_HEAD_2:
            if data == FRAME_HEAD_2:
                state = READING_DATA
                data_buf = bytearray()
        elif state == READING_DATA:
            data_buf.append(data[0])
            if len(data_buf) == 4:
                print('Down: ', FRAME_HEAD, data_buf)
                down_data = struct.unpack('<hh', data_buf)
                print(down_data)
                state = WAITING_FRAME_HEAD_1
                time.sleep(1)
                down_ser.write(FRAME_HEAD + b'\x00\x01\x02')

    if state == WAITING_FRAME_HEAD_1:
        data_buf = bytearray()
