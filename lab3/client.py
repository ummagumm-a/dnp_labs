import zmq
import threading
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('client_input_port', type=int)
    parser.add_argument('client_outputs_port', type=int)
    args = parser.parse_args()

    context = zmq.Context()

    client_input = context.socket(zmq.SUB)
    client_input.connect(f'tcp://localhost:{args.client_input_port}')
    client_input.setsockopt_string(zmq.SUBSCRIBE, '')
    client_input.RCVTIMEO = 1000

    client_outputs = context.socket(zmq.PUB)
    client_outputs.connect(f'tcp://localhost:{args.client_outputs_port}')

    run_event = threading.Event()
    run_event.set()
    def recv(run_event):
        while run_event.is_set():
            try:
                response = client_input.recv()
                print(response)
            except zmq.error.Again:
                continue

    recv_thread = threading.Thread(target=recv, args=(run_event,))
    recv_thread.start()
    try:
        while True:
            line = input()
            client_outputs.send(line.encode())
    except KeyboardInterrupt:
        print("Graceful shutdown...")
    finally:
        run_event.clear()
        recv_thread.join()
        client_input.close()
        client_outputs.close()
        context.term()