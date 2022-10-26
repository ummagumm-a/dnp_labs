import raft_pb2_grpc as pb2_grpc
import raft_pb2 as pb2
import grpc


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
        return f'{reply.leader_id} {reply.leader_address}'

    def suspend(self, period: int):
        _ = self.stub.suspend(pb2.SuspendRequest(period=period))


def cli_loop():
    connection = ClientConnection()
    while True:
        try:
            inp = input("> ")
            if len(inp.split()) == 1:
                query = inp
                arg = None
            else:
                query, arg = inp.split()

            if query == 'connect':
                connection.connect(arg)
            elif query == 'getleader':
                resp = connection.get_leader()
                print(resp)
            elif query == 'suspend':
                connection.suspend(int(arg))
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
