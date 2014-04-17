import serial
import mapper

dev = mapper.device("test")
sensor1 = dev.add_output("/outsig", 1, "i", None, 0, 1023)

ser = serial.Serial("/dev/ttyACM0", 115200)

while True:
    dev.poll(0)
    v1 = int(ser.readline())
    print v1
    sensor1.update(v1)
