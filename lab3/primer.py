import zmq
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('worker_input_port', type=int)
    parser.add_argument('worker_output_port', type=int)
    args = parser.parse_args()

    context = zmq.Context()

    worker_input = context.socket(zmq.SUB)
    worker_input.connect(f'tcp://localhost:{args.worker_input_port}')
    worker_input.setsockopt_string(zmq.SUBSCRIBE, 'is prime')

    worker_output = context.socket(zmq.PUSH)
    worker_output.connect(f'tcp://localhost:{args.worker_output_port}')

    def is_prime(n):
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        for divisor in range(3, n, 2):
            if n % divisor == 0:
                return False
        return True

    while True:
        msg = worker_input.recv()
        msg = msg.decode()
        num = int(msg[len('is prime '):])

        if is_prime(num):
            worker_output.send(f'{num} is prime'.encode())
        else:
            worker_output.send(f'{num} is not prime'.encode())
