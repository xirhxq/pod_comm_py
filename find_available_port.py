import glob

serial_ports = glob.glob('/dev/tty*')
for port in serial_ports:
    print(port)

# in terminal: ls /dev/tty*