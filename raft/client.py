import raft_pb2_grpc as pb2_grpc
import raft_pb2 as pb2
import grpc
import logging
import sys

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(message)s")
# log to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)


class ClientConnection:
    def __init__(self):
        self.server_address = None
        self.stub = None

    def connect(self, server_address: str):
        self.server_address = server_address
        channel = grpc.insecure_channel(server_address)
        self.stub = pb2_grpc.RaftStub(channel)

    def get_leader(self):
        reply = self.stub.get_leader(pb2.EmptyMessage())
        if hasattr(reply, 'leader'):
            return f'{reply.leader.leader_id} {reply.leader.leader_address}'
        else:
            return 'No leader yet'

    def suspend(self, period: float):
        _ = self.stub.suspend(pb2.SuspendRequest(period=period))

    def setval(self, key: str, value: str):
        reply = self.stub.setval(pb2.LogEntry(key=key, value=value))

        return str(reply.is_success)

    def getval(self, key: str):
        reply = self.stub.getval(pb2.GetValRequest(key=key))

        return str(reply.is_success) + ' ' + reply.value


def cli_loop():
    logger.info("The client starts")
    connection = ClientConnection()
    while True:
        try:
            inp = input("> ")
            if len(inp.split()) == 1:
                query = inp
                args = None
            else:
                query, args = inp.split()[0], inp.split()[1:]

            if query == 'connect':
                connection.connect(':'.join(args))
            elif query == 'getleader':
                resp = connection.get_leader()
                print(resp)
            elif query == 'suspend':
                connection.suspend(float(args[0]))
            elif query == 'setval':
                resp = connection.setval(args[0], args[1])
                print(resp)
            elif query == 'getval':
                resp = connection.getval(args[0])
                print(resp)
            elif query == 'quit':
                break
            else:
                print("Incorrect Query")
                continue
        except KeyboardInterrupt:
            print("CLIENT SHUTTING DOWN")
            break


if __name__ == '__main__':
    cli_loop()
