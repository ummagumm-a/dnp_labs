import zmq
import argparse
import threading

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--client_input_port', default=5000, type=int, required=False)
    parser.add_argument('--client_outputs_port', default=5001, type=int, required=False)
    parser.add_argument('--worker_input_port', default=5002, type=int, required=False)
    parser.add_argument('--worker_outputs_port', default=5003, type=int, required=False)
    args = parser.parse_args()

    context = zmq.Context()

    # # create sockets
    client_input = context.socket(zmq.PUB)
    client_input.bind(f'tcp://*:{args.client_input_port}')
    client_outputs = context.socket(zmq.REP)
    client_outputs.bind(f'tcp://*:{args.client_outputs_port}')

    worker_input = context.socket(zmq.PUB)
    worker_input.bind(f'tcp://*:{args.worker_input_port}')
    worker_outputs = context.socket(zmq.SUB)
    worker_outputs.bind(f'tcp://*:{args.worker_outputs_port}')
    worker_outputs.setsockopt_string(zmq.SUBSCRIBE, '')
    worker_outputs.RCVTIMEO = 1000

    # launch server
    run_event = threading.Event()
    run_event.set()
    def recv(run_event):
        while run_event.is_set():
            try:
                msg = worker_outputs.recv()
                client_input.send(msg)
            except zmq.error.Again:
                continue

    recv_thread = threading.Thread(target=recv, args=(run_event,))
    recv_thread.start()
    try:
        while True:
            msg = client_outputs.recv()
            client_outputs.send(b'ack')

            worker_input.send(msg)
            client_input.send(msg)
            
    except KeyboardInterrupt:
        print("Graceful shutdown...")
    finally:
        run_event.clear()
        recv_thread.join()
        client_input.close()
        client_outputs.close()
        worker_input.close()
        worker_outputs.close()
        context.term()
