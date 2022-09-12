import socket
import argparse

BUF_SIZE = 1024
TIMEOUT = 5

# numbers = [2147483477, 2147483137, 2147482943,
#            2147482801, 2147482583, 2147482343,
#            2147482081, 2147481893, 2147481563,
#            2147481337, 2147481173, 2147480969]
numbers = [15492781, 15492787, 15492803,
           15492811, 15492810, 15492833,
           15492859, 15502547, 15520301,
           15527509, 15522343, 1550784]

def send_number(number, address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        s.settimeout(TIMEOUT)
        s.sendall(number.to_bytes(4, byteorder='big'))
        data = s.recv(BUF_SIZE)
        print(f'received: {data.decode()}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server_address', type=str)
    args = parser.parse_args()

    # parse server_address
    server_host, server_port = args.server_address.split(':')
    server_port = int(server_port)

    for number in numbers:
        print(f'sending {number}')
        send_number(number, (server_host, server_port))
