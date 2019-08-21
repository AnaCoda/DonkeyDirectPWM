import pygame
import win32api
import win32gui
import socket
import sys
from time import sleep

max_y = 700
max_x = 800
circle_size = 20

def get_constants(prefix):
    """Create a dictionary mapping socket module constants to their names."""
    return dict( (getattr(socket, n), n)
                 for n in dir(socket)
                 if n.startswith(prefix)
                 )

families = get_constants('AF_')
types = get_constants('SOCK_')
protocols = get_constants('IPPROTO_')

# Create a TCP/IP socket
sock = socket.create_connection(('192.168.3.200', 10000))

print ('Family  :', families[sock.family])
print ('Type    :', types[sock.type])
print ('Protocol:', protocols[sock.proto])

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def main():
    pygame.init()
    size = max_x, max_y

    old_vert_val = 0
    old_hor_val = 0

    screen = pygame.display.set_mode(size)

    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (0, 0, 0), (max_x/2, 0), (max_x/2, max_y))
    pygame.draw.line(screen, (0, 0, 0), (0, max_y/2), (max_x, max_y/2))
    pygame.draw.circle(screen, (255, 0, 0), (int(max_x/2), int(max_y/2)), circle_size)
    pygame.draw.rect(screen, (0, 0, 255), (0, 500, 200, max_y))
    pygame.mouse.set_pos([max_x/2, max_y/2])

    pygame.display.flip()

    
    while True:
        panic = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pygame.display.update()
        point = pygame.mouse.get_pos()
        x_coord, y_coord = point
        if(x_coord < 200 and y_coord > 500):
            sleep(0.2)
            pygame.mouse.set_pos([max_x/2, max_y/2])
            sleep(0.2)
        a = win32api.GetKeyState(0x01)
        if a < 0:
            point = (0, 0)
            point = pygame.mouse.get_pos()
            x_coord, y_coord = point
            if(x_coord < 200 and y_coord > 500):
                panic = 1
            print(point)
            screen.fill((255, 255, 255))
            pygame.draw.line(screen, (0, 0, 0), (max_x/2, 0), (max_x/2, max_y))
            pygame.draw.line(screen, (0, 0, 0), (0, max_y/2), (max_x, max_y/2))
            pygame.draw.rect(screen, (0, 0, 255), (0, 500, 200, max_y))
            pygame.draw.circle(screen, (255, 0, 0), point, 20)
            vert_val = translate(y_coord, max_y, 0, -1, 1)
            hor_val = translate(x_coord, 0, max_x, -1, 1)
            print(str(hor_val) + ", " + str(vert_val))
        else:
            point = (0, 0)
            point = pygame.mouse.get_pos()
            x_coord, y_coord = point
            pygame.mouse.set_pos([max_x/2, y_coord])
            point = pygame.mouse.get_pos()
            x_coord, y_coord = point
            print(point)
            screen.fill((255, 255, 255))
            pygame.draw.line(screen, (0, 0, 0), (max_x/2, 0), (max_x/2, max_y))
            pygame.draw.line(screen, (0, 0, 0), (0, max_y/2), (max_x, max_y/2))
            pygame.draw.rect(screen, (0, 0, 255), (0, 500, 200, max_y))
            pygame.draw.circle(screen, (255, 0, 0), point, 20)
            vert_val = translate(y_coord, max_y, 0, -1, 1)
            hor_val = translate(x_coord, 0, max_x, -1, 1)
        
        if(panic == 1):
            sock.sendall('p\n'.encode())
        elif(old_hor_val != hor_val and old_vert_val != vert_val):
            sock.sendall(("s" + str(vert_val) + "d" + str(hor_val) + "\n").encode())
        old_vert_val = vert_val
        old_hor_val = hor_val

main()