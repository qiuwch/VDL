# A simple script to test the upper bound socket communication speed we can achieve
import argparse
import socket, sys
sys.path.append('..')
from util import Timer, Counter
import numpy as np

send_timer = Timer("Communication")
throughput_counter = Counter("Network Throughput")

port = 10010
def server():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', port))
    listen_socket.listen(5)

    connection, addr = listen_socket.accept()
    while True:
        data = connection.recv(1000)
        if not data:
            print 'Done'
            break

def client(server_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    send(client_socket, 1000, 1000)
    client_socket.close()

def send(client_socket, size, count):
    for i in range(count):
        random_array = np.random.rand((size))
        payload = random_array.tobytes()
        send_timer.tic()
        client_socket.send(payload)
        send_timer.toc()
        throughput_counter.add(len(payload))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client')
    args = parser.parse_args()

    if args.server:
        server()

    if args.client:
        server_ip = args.client
        client(server_ip)
        print throughput_counter
        print send_timer
        print 'Speed: %.2fKB/s' % (throughput_counter.sum / send_timer.total / 1000)

if __name__ == '__main__':
    main()
