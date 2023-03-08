import serial
from time import sleep
 
if __name__=="__main__":
    serial = serial.Serial("/dev/pts/1", 115200, timeout=0.5)
    if serial.isOpen():
        print("open success")
    else:
        print("open failed")
 
    while True:
        str = b"\x05\xAA\x00\x01\x02\x03\x04"
        serial.write(str)
        print("send: ", str)
        sleep(1)