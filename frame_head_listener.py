import serial

# 定义帧头
FRAME_HEAD_1 = b'\x05'
FRAME_HEAD_2 = b'\xAA'

# 定义状态机状态
WAITING_FRAME_HEAD_1 = 1
WAITING_FRAME_HEAD_2 = 2
READING_DATA = 3

# 定义串口参数
ser = serial.Serial(
    port='/dev/pts/2',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.5
)

# 初始化状态机状态
state = WAITING_FRAME_HEAD_1

# 初始化数据缓冲区
data_buf = bytearray()

while True:
    # 读取一个字节的数据
    data = ser.read(1)

    # 判断数据是否为空
    if data:
        # 根据状态机状态进行处理
        if state == WAITING_FRAME_HEAD_1:
            if data == FRAME_HEAD_1:
                state = WAITING_FRAME_HEAD_2
        elif state == WAITING_FRAME_HEAD_2:
            if data == FRAME_HEAD_2:
                state = READING_DATA
                data_buf = bytearray()
        elif state == READING_DATA:
            data_buf.append(data[0])
            if len(data_buf) == 5:
            # 在这里可以判断数据是否已经接收完整
            # 如果已经接收完整，可以对数据进行处理
            # 处理完后，将状态机状态置为WAITING_FRAME_HEAD_1，等待下一帧数据的到来
            # ...
                print('get one', data_buf)
                state = WAITING_FRAME_HEAD_1

    # 处理完一帧数据后，清空数据缓冲区
    if state == WAITING_FRAME_HEAD_1:
        data_buf = bytearray()
