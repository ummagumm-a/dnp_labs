import random
from utils import parse_conf
import sys
import logging
import grpc
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc
from threading import Thread, Event, Lock, Timer
import time

# TODO: разобраться с термами

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
        self.servers_info = parse_conf(config_path)
        self.stubs = self._make_stubs()
        self.state = ServerStates.FOLLOWER
        # This thread pool is maintained for sending requests for votes to all other nodes.
        self.pool = ThreadPoolExecutor(max_workers=len(self.servers_info))
        self.leader_id = None
        # This field is required to know whether a leader is alive or there is an election in progress.
        # If a leader is alive right now then it will be an 'append_entries'
        # If leader has died and the election is in progress
        # then that node would receive a 'request_vote' message.
        self.last_received_message_type = None
        # All operations should be mutually exclusive,
        self.mutex = Lock()

        # get addresses of other nodes
        server_addresses = self.servers_info.values()
        # remove itself from the list of addresses
        self.other_addresses = list(filter(lambda x: x != self.servers_info[server_id], server_addresses))

        self.run_event = Event()

        self.election_loop_thread_handler = Timer(2, self._election_timeout_loop)
        self.election_loop_thread_handler.start()

        self.heartbeat_if_leader_thread_handler = Timer(2, self._heartbeat_if_leader)
        self.heartbeat_if_leader_thread_handler.start()

        self.previous_reset_time = time.monotonic()
        self.run_event.set()
        self.is_suspended = False
        self.heartbeat_interval = 0.05

        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def _make_stubs(self):
        stubs = { address: pb2_grpc.RaftStub(grpc.insecure_channel(address))
                  for address in self.servers_info.values() }
        return stubs

    def _send_request_for_vote(self, address):
        try:
            request = pb2.RequestVoteRequest(term=self.term, candidate_id=self.server_id)
            reply = self.stubs[address].request_vote(request)
            logger.debug(reply)

            return reply.term, int(reply.result)
        except grpc._channel._InactiveRpcError:
            return self.term, 0

    def _start_election(self):
        """
        When a node becomes Candidate, it should send 'request_vote' messages to every other node in the system.

        """
        self.term += 1
        # send requests for votes to other nodes
        timeout = max(0.0, self.election_timeout - (time.monotonic() - self.previous_reset_time))
        answers = self.pool.map(self._send_request_for_vote, self.other_addresses, timeout=timeout)
        pos_answers = 0
        try:
            # collect replies
            for term, ans in answers:
                if term > self.term:
                    break
                pos_answers += ans

                if pos_answers == len(self.servers_info) // 2:
                    logger.info("Votes received")
                    self.previous_reset_time = time.monotonic()
                    self.state = ServerStates.LEADER
                    logger.info(f"I am a {self._whoami()}. Term: {self.term}")
                    logger.debug('return')
                    return
        except futures._base.TimeoutError:
            pass
        logger.info("Votes received")
        logger.debug("Candidate to follower")
        # TODO: is it correct? Should I increment the term? Should I reset 'voted_for'?
        self.election_timeout = random.random() * 0.15 + 0.15
        self.state = ServerStates.FOLLOWER
        self.voted_for = None
        self.previous_reset_time = time.monotonic()

        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def _whoami(self):
        if self.state == ServerStates.FOLLOWER:
            return 'FOLLOWER'
        elif self.state == ServerStates.CANDIDATE:
            return 'CANDIDATE'
        elif self.state == ServerStates.LEADER:
            return 'LEADER'

    def _set_voted_for(self, server_id):
        self.voted_for = server_id
        logger.info(f"Voted for node {server_id}")

    def _election_timeout_loop(self):
        self.run_event.wait()
        while self.run_event.is_set():
            self.mutex.acquire()
            # if didn't receive messages for longer than specified timeout
            if time.monotonic() - self.previous_reset_time > self.election_timeout and \
                    self.state == ServerStates.FOLLOWER and \
                    self.voted_for is None and \
                    not self.is_suspended:
                logger.debug(f"{self.election_timeout}")
                # if this node is a follower - become candidate and start election
                logger.info(f"The leader is dead.")
                logger.debug(f"Follower to candidate, term: {self.term}")

                # transition to the candidate state
                self.state = ServerStates.CANDIDATE
                # vote for yourself
                self._set_voted_for(self.server_id)
                logger.info(f"I am a {self._whoami()}. Term: {self.term}")
                self.previous_reset_time = time.monotonic()
                # start new election
                self._start_election()
                logger.debug(f"Time left: {time.monotonic() - self.previous_reset_time}")

            self.mutex.release()

    def _heartbeat_if_leader(self):
        self.run_event.wait()
        while self.run_event.is_set():
            # If server is a Leader
            self.mutex.acquire()
            if self.state == ServerStates.LEADER and not self.is_suspended:
                # For every server in the system
                request = pb2.AppendEntryRequest(term=self.term, leader_id=self.server_id)
                logger.debug(f"voted for: {self.voted_for}, term: {self.term}")

                def helper(address):
                    try:
                        logger.debug(f'Sending heartbeat message to {address}')
                        reply = self.stubs[address].append_entries(request, timeout=self.heartbeat_interval)
                        logger.debug(f'Sent heartbeat message to {address}')
                        logger.debug(str(reply))

                        return reply.success, reply.term
                    except grpc._channel._InactiveRpcError:
                        logger.debug('loh')
                        return True, 0
                    except grpc.RpcError as e:
                        logger.debug('dksjflsekj')
                        logger.debug(str(e))
                        return True, 0

                replies = self.pool.map(helper, self.other_addresses)
                for success, reply_term in replies:
                    # If leader receives a term number that is greater than its own - turn into a follower
                    if not success or reply_term > self.term:
                        self.term = reply_term
                        self.state = ServerStates.FOLLOWER
                        self.voted_for = None
                        logger.info(f"I am a {self._whoami()}. Term: {self.term}")
                        self.previous_reset_time = time.monotonic()
                        break

                # Every 'heartbeat interval' seconds
                time.sleep(self.heartbeat_interval)
            self.mutex.release()

    def append_entries(self, request, context):
        start_time = time.monotonic()
        logger.debug("heartbeat start")
        self.mutex.acquire()
        # if this node is suspended - return an error
        if self.is_suspended:
            logger.debug("return error")
            self.mutex.release()
            context.abort(grpc.StatusCode.UNAVAILABLE, 'I am suspended.')

        logger.debug(f"heartbeat: {time.monotonic() - start_time}")
        logger.debug(str(request))

        if self.term > request.term:
            reply = pb2.AppendEntryReply(term=self.term, success=False)
        elif self.term < request.term:
            # if receives a heartbeat from another Leader with term number greater than its own - turn into a follower
            self.term = request.term
            self.state = ServerStates.FOLLOWER
            self.voted_for = None
            self.leader_id = request.leader_id
            logger.info(f"I am a {self._whoami()}. Term: {self.term}")
            reply = pb2.AppendEntryReply(term=self.term, success=True)
        else:
            reply = pb2.AppendEntryReply(term=self.term, success=True)

        # update time of last received message and its type
        self.previous_reset_time = time.monotonic()
        self.last_received_message_type = 'append_entries'

        self.mutex.release()
        return reply

    def request_vote(self, request, context):
        self.mutex.acquire()
        # if this node is suspended - return an error
        if self.is_suspended:
            logger.debug("return error")
            self.mutex.release()
            context.abort(grpc.StatusCode.UNAVAILABLE, 'I am suspended.')
        """
        Candidate server should call this function in order to collect a vote from this server.
        """
        logger.debug("request_vote")
        logger.debug(str(request))
        # update timer because a new message is received
        self.previous_reset_time = time.monotonic()
        self.last_received_message_type = 'request_vote'

        # if term of candidate is greater
        if self.term < request.term:
            # update your own term
            self.term = request.term
            # server becomes a follower
            self.state = ServerStates.FOLLOWER

            self._set_voted_for(request.candidate_id)
            logger.info(f"I am a {self._whoami()}. Term: {self.term}")

            # send positive answer
            reply = pb2.RequestVoteReply(term=self.term, result=True)

        # if server and candidate are in the same term and server didn't yet vote for anyone in this term
        elif self.term == request.term and self.voted_for is None and self.state != ServerStates.LEADER:
            # server saves info that it voted for this candidate
            self._set_voted_for(request.candidate_id)

            # send positive answer
            reply = pb2.RequestVoteReply(term=self.term, result=True)
        else:
            # send negative answer
            reply = pb2.RequestVoteReply(term=self.term, result=False)

        self.mutex.release()
        return reply

    def get_leader(self, request, context):
        """
        Returns the current leader in the system.
        If leader is alive - send id and address of this leader.
        If election is in progress - send id and address of the node that this node voted for.
        If node didn't vote in this term yet - return nothing.
        """

        if self.state == ServerStates.LEADER:
            return pb2.GetLeaderReply(leader=pb2.GetLeaderPosAnswer(
                    leader_id=self.server_id,
                    leader_address=self.servers_info[self.server_id]
                ))
        elif self.last_received_message_type == 'append_entries':
            # If there is a leader in the system
            return pb2.GetLeaderReply(leader=pb2.GetLeaderPosAnswer(
                    leader_id=self.leader_id,
                    leader_address=self.servers_info[self.leader_id]
                ))
        elif self.last_received_message_type == 'request_vote':
            # That would mean that previous leader has died, so election is in progress
            return pb2.GetLeaderReply(leader=pb2.GetLeaderPosAnswer(
                    leader_id=self.voted_for,
                    leader_address=self.servers_info[self.voted_for]
                ))
        else:
            return pb2.GetLeaderReply(empty_message=pb2.EmptyMessage())

    def shutdown(self):
        self.run_event.clear()
        self.pool.shutdown()

    def _reset(self):
        self.term = 0
        self.voted_for = 0
        self.state = ServerStates.FOLLOWER
        self.election_timeout = random.random() * 0.15 + 0.15

        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def suspend(self, request, context):
        self.is_suspended = True
        logger.info(f"Suspending for {request.period} seconds")
        time.sleep(request.period)
        self._reset()
        self.is_suspended = False
        logger.info("Suspend out")

        return pb2.EmptyMessage()


def which_address(config_path, server_id):
    server_address = parse_conf(config_path)[server_id]
    try:
        logger.info(f"The server starts at {server_address}")
    except KeyError:
        logger.error("No server with such id. Check config.conf for available ids.")
        sys.exit()

    return server_address


if __name__ == '__main__':
    config_path = 'config.conf'
    server_id = int(sys.argv[1])
    # Print the address of this server
    server_address = which_address(config_path, server_id)

    # setup and run server
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server = Server(server_id, config_path)
    try:
        pb2_grpc.add_RaftServicer_to_server(server, grpc_server)
        grpc_server.add_insecure_port(server_address)

        grpc_server.start()
        grpc_server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutdown...")
        server.shutdown()
        grpc_server.stop(3)

