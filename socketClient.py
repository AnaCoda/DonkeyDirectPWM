import socket
import sys

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

# Send data
message = 'This is the message.  It will be repeated.'
print ('sending "%s"' % message)
sock.sendall(message.encode('utf-8'))
data2 = 'more text'
amount_received = 0
amount_expected = len(message + data2)
while True:
    data = sock.recv(16)
    amount_received += len(data)
    print ('received "%s"' % data.decode('utf-8'))