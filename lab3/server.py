import zmq
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('client_input_port', type=int)
    parser.add_argument('client_outputs_port', type=int)
    parser.add_argument('worker_input_port', type=int)
    parser.add_argument('worker_outputs_port', type=int)
    args = parser.parse_args()

    context = zmq.Context()

    # create sockets
    client_input = context.socket(zmq.PUB)
    client_input.bind(f'tcp://*:{args.client_input_port}')

    client_outputs = context.socket(zmq.SUB)
    client_outputs.bind(f'tcp://*:{args.client_outputs_port}')
    client_outputs.setsockopt_string(zmq.SUBSCRIBE, '')

    worker_input = context.socket(zmq.PUB)
    worker_input.bind(f'tcp://*:{args.worker_input_port}')
    worker_outputs = context.socket(zmq.PULL)
    worker_outputs.bind(f'tcp://*:{args.worker_outputs_port}')

    # launch server
    while True:
        msg = client_outputs.recv()
        msgd = msg.decode()
        if msgd.startswith('is prime') or msgd.startswith('gcd'):
            worker_input.send(msg)
            msg = worker_outputs.recv()

        client_input.send(msg)


