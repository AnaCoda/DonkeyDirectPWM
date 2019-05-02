import socket
import sys
from sendPWMToCar import *

steering_controller = piDirectPWM(18)
throttle_controller = piDirectPWM(13)

steering = PWMSteering(controller=steering_controller)
throttle = PWMThrottle(controller=throttle_controller)

def parse(buf):
    speed = ''
    direction = ''
    index = 0
    if(buf[index] == 'p'):
        return "PANIC"
    if(buf[index] == 's'):
        index += 1
        while(buf[index] != 'd'):
            speed += buf[index]
            index += 1
        while(buf[index] != '\n'):
            if(buf[index] == 'd'):
                index += 1
            direction += buf[index]
            index += 1
    return [float(speed), float(direction)]

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('192.168.3.200', 10000)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
dataBuf = ""
while True:
    # Wait for a connection
    print ('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print ('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1)
            dataBuf += data.decode()
            if(data.decode() == '\n'):
               # print(dataBuf)
                speedDir = parse(dataBuf)
                dataBuf = ''
                if(speedDir == "PANIC"):
                    print("PANIC")
                else:
                    print("Speed: " + str(speedDir[0]) + "\nDirection: " + str(speedDir[1]))
                    steering.run(speedDir[1])
                    print("pp")
                    print(throttle.run(speedDir[0]))
    finally:
        # Clean up the connection
        connection.close()
