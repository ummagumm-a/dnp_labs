from queue import Queue, Empty, Full
from typing import Tuple
import socket
from threading import Thread, Event
from time import sleep
import logging
import argparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SERVER_HOST = '127.0.0.1'
BUF_SIZE = 1024
NUM_WORKER_THREADS = 5

queue = Queue(1024)

def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True

def process_connection(run_event):
    while run_event.is_set():
        try:
            (conn, address) = queue.get(timeout=1)
        except Empty as e:
            continue

        data = conn.recv(BUF_SIZE)
        int_data = int.from_bytes(data, byteorder='big')
        if is_prime(int_data):
            conn.sendall(f'{int_data} is prime'.encode())
        else:
            conn.sendall(f'{int_data} is not prime'.encode())

        queue.task_done()

worker_threads = []
run_event = Event()
run_event.set()
for i in range(NUM_WORKER_THREADS):
    worker = Thread(target=process_connection, args=(run_event,))
    worker.start()
    worker_threads.append(worker)

def run_server(port_number):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_HOST, port_number))
        s.listen()
        logger.info("Server started")

        try:
            while True:
                conn, address = s.accept()
                try:
                    queue.put_nowait((conn, address))
                except Full:
                    logger.warning('Queue is full.')
                    continue
                logger.debug(f'Queue size: {queue.qsize()}.')
        except KeyboardInterrupt as inter:
            logger.info("Graceful shutdown")
            queue.join()
            run_event.clear()
            for worker in worker_threads:
                worker.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server_port', type=int)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    run_server(args.server_port)
