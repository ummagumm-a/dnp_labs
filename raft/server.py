import random
from utils import parse_conf
import sys
import logging
import grpc
from concurrent import futures
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(message)s")
# log to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)


class ServerStates:
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


class Server(pb2_grpc.RaftServicer):
    def __init__(self, server_id: int, config_path: str):
        self.term = 0
        self.server_id = server_id
        self.election_timeout = random.random()
        self.servers_info = parse_conf(config_path)
        self.state = ServerStates.FOLLOWER


if __name__ == '__main__':
    config_path = 'config.conf'
    server_id = int(sys.argv[1])

    server = Server(server_id, config_path)
    try:
        server_address = server.servers_info[server_id]
    except KeyError:
        logger.error("No server with such id. Check config.conf for available ids.")
        sys.exit()

    try:
        # setup and run server
        grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_RaftServicer_to_server(server, grpc_server)
        grpc_server.add_insecure_port(server_address)
        logger.info(f"Server is started at {server_address}")
        grpc_server.start()
        grpc_server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutdown...")

