import serial

ser = serial.Serial('/dev/pts/2', 115200, timeout=0.5)

while True:
    FRAME_HEAD = b'\x05\xaa'
    header = ser.read_until(FRAME_HEAD)  # 监听到帧头
    if header == FRAME_HEAD:
        data = ser.read(5)  # 接收5个字节的数据
        print(f'header = {header}')
        print(f'data = {data}')
    else:
        print(f'header = {header}')
