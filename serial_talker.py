import serial
from time import sleep
import struct

FRAME_HEAD_1 = b'\xEB'
FRAME_HEAD_2 = b'\x90'
FRAME_HEAD = FRAME_HEAD_1 + FRAME_HEAD_2
 
if __name__=="__main__":
    # /dev/pts/1 on Ubuntu & /dev/ttys003 on MacOS
    serial = serial.Serial("/dev/ttys002", 115200, timeout=0.5)
    if serial.isOpen():
        print("open success")
    else:
        print("open failed")
 
    while True:
        pitch, yaw = map(float, input().split())
        str = struct.pack('<hh', int(pitch * 100), int(yaw * 100))
        serial.write(FRAME_HEAD + str)
        print("send: ", str)
        sleep(1)