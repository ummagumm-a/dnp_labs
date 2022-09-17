import zmq
import math
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('worker_input_port', type=int)
    parser.add_argument('worker_output_port', type=int)
    args = parser.parse_args()

    context = zmq.Context()

    worker_input = context.socket(zmq.SUB)
    worker_input.connect(f'tcp://localhost:{args.worker_input_port}')
    worker_input.setsockopt_string(zmq.SUBSCRIBE, 'gcd')

    worker_output = context.socket(zmq.PUSH)
    worker_output.connect(f'tcp://localhost:{args.worker_output_port}')

    def parse_message(msg):
        nums = msg.split()[1:]
        nums = list(map(int, nums))

        return nums[0], nums[1]

    while True:
        msg = worker_input.recv()
        msg = msg.decode()

        try:
            num1, num2 = parse_message(msg)
        except:
            worker_output.send(f'incorrect message format: {msg}'.encode())
            continue

        worker_output.send(f'gcd for {num1} and {num2} is {math.gcd(num1, num2)}'.encode())
