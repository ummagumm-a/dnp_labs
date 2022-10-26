import random
from utils import parse_conf
import sys
import logging
import grpc
from concurrent import futures
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc
from threading import Thread, Event
import time

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
        self.voted_for = None
        self.server_id = server_id
        self.election_timeout = random.random() * 0.15 + 0.15
        self.previous_reset_time = time.monotonic()
        self.servers_info = parse_conf(config_path)
        self.state = ServerStates.FOLLOWER
        self.run_event = Event()
        self.run_event.set()

        self.election_loop_thread_handler = Thread(target=self._election_timeout_loop)
        self.election_loop_thread_handler.start()

    def _election_timeout_loop(self):
        while self.run_event.is_set():
            if time.monotonic() - self.previous_reset_time > self.election_timeout:
                if self.state == ServerStates.FOLLOWER:
                    self.previous_reset_time = time.monotonic()
                    self.state = ServerStates.CANDIDATE
                    self.voted_for = self.server_id
                    self.term += 1

    def append_entries(self, request, context):
        self.previous_reset_time = time.monotonic()

    def request_vote(self, request, context):
        """
        Candidate server should call this function in order to collect a vote from this server.
        """

        # update timer because a new message is received
        self.previous_reset_time = time.monotonic()

        # if term of candidate is greater
        if self.term < request.term:
            # update your own term
            self.term = request.term
            self.voted_for = None
            # server becomes a follower
            self.state = ServerStates.FOLLOWER

        # if server and candidate are in the same term and server didn't yet vote for anyone in this term
        if self.term == request.term and self.voted_for is None:
            # server saves info that it voted for this candidate
            self.voted_for = request.candidate_id

            return pb2.RequestVoteReply(term=self.term, result=True)
        else:
            return pb2.RequestVoteReply(term=self.term, result=False)

    def shutdown(self):
        self.run_event.clear()


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
        server.shutdown()

