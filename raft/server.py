import collections
import random
from utils import parse_conf
import sys
import logging
import grpc
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc
from threading import Event, Lock, Timer
import time

# setup logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(message)s")
# log to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)


class ServerStates:
    """
    Server can be in one of these states.
    """
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


LogEntry = collections.namedtuple("LogEntry", ['index', 'term', 'log'])


class Server(pb2_grpc.RaftServicer):
    def __init__(self, server_id: int, config_path: str):
        # term defines how many elections there were in the system
        self.term = 0
        # the last node that this one voted for
        self.voted_for = None
        # id of this server
        self.server_id = server_id
        # if this node doesn't receive any message for this period, it turns into the candidate
        self.election_timeout = None
        self._reset_election_timeout()
        # information about system - ids and addresses of all nodes
        self.servers_info = parse_conf(config_path)
        # state of this node
        self.state = ServerStates.FOLLOWER
        # This thread pool for sending messages to all other nodes.
        self.pool = ThreadPoolExecutor(max_workers=len(self.servers_info))
        # id of leader in the system
        self.leader_id = None
        # This field is required to know whether a leader is alive or there is an election in progress.
        # If a leader is alive right now then it will be an 'append_entries'
        # If leader has died and the election is in progress
        # then that node would receive a 'request_vote' message.
        self.last_received_message_type = None
        # All operations should be mutually exclusive,
        # so that node state is always consistent
        self.mutex = Lock()

        # get addresses of all nodes
        server_addresses = self.servers_info.values()
        # remove itself from the list of addresses
        self.other_addresses = list(filter(lambda x: x != self.servers_info[server_id], server_addresses))
        # stubs to all other nodes in the system
        self.stubs = self._make_stubs()

        # server runs until this variable is 'unset'. Required for graceful shutdown of the server
        self.run_event = Event()

        # Run thread which checks for timeout and runs elections
        self.election_loop_thread_handler = Timer(2, self._election_timeout_loop)
        self.election_loop_thread_handler.start()

        # Run thread which sends heartbeats if this node is a leader
        self._send_heartbeats_flag = Event()
        self._send_heartbeats_flag.clear()
        self.heartbeat_if_leader_thread_handler = Timer(2, self._heartbeat_if_leader)
        self.heartbeat_if_leader_thread_handler.start()

        # The time of last received message. Required for timeout detection.
        self.previous_reset_time = time.monotonic()
        self.run_event.set()
        # A client can suspend nodes from the outside. If set to true, the server becomes not responsive.
        self.is_suspended = False
        # Time period between heartbeats sent by a leader
        self.heartbeat_interval = 0.05

        # Logs. Each entry is of the form: (index, term_number, command)
        self.log_entries = []
        self.commit_index = 0
        self.next_index = { address: 0 for address in self.other_addresses }
        self.match_index = { address: 0 for address in self.other_addresses }
        self.committed_events = {}

        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def _reset_election_timeout(self):
        self.election_timeout = random.uniform(0.15, 0.3)

    def _make_stubs(self):
        """
        Create stubs to all other nodes in the system.
        """
        stubs = {address: pb2_grpc.RaftStub(grpc.insecure_channel(address))
                 for address in self.other_addresses}
        return stubs

    def _send_request_for_vote(self, address):
        """
        Send a request for vote to a node located at 'address'.
        """
        try:
            request = pb2.RequestVoteRequest(term=self.term, candidate_id=self.server_id)
            reply = self.stubs[address].request_vote(request)
            logger.debug(reply)

            return reply.term, int(reply.result)
        except grpc._channel._InactiveRpcError:
            return self.term, 0
        except grpc.RpcError as e:
            logger.debug('dksjflsekj')
            logger.debug(str(e))
            return 0, 0

    def _become_follower(self):
        """
        Turn into a follower and update state accordingly.
        """
        self._send_heartbeats_flag.clear()
        self._reset_election_timeout()
        self.state = ServerStates.FOLLOWER
        self.voted_for = None
        self.previous_reset_time = time.monotonic()
        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def _become_candidate(self):
        """
        Turn into a candidate and update state accordingly.
        """
        self.state = ServerStates.CANDIDATE
        self.term += 1
        # vote for yourself
        self._set_voted_for(self.server_id)
        self.previous_reset_time = time.monotonic()
        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def _become_leader(self):
        self.previous_reset_time = time.monotonic()
        self.state = ServerStates.LEADER
        self._send_heartbeats_flag.set()
        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

    def _start_election(self):
        """
        When a node becomes Candidate, it should send 'request_vote' messages to every other node in the system.

        """

        # Define timeout after which this node should give up on collecting votes
        # and turn into a follower
        timeout = max(0.0, self.election_timeout - (time.monotonic() - self.previous_reset_time))
        # send requests for votes to other nodes
        answers = self.pool.map(self._send_request_for_vote, self.other_addresses, timeout=timeout)
        # number of positive votes which came from other nodes
        pos_answers = 0
        try:
            # collect replies
            for term, ans in answers:
                # if there is a node with term number higher than this node's
                if term > self.term:
                    self.term = term
                    break
                pos_answers += ans

                # if half of nodes sent a positive vote (it is enough to say that this node got majority of nodes)
                if pos_answers == len(self.servers_info) // 2:
                    # reset timer and turn into a leader
                    logger.info("Votes received")
                    self._become_leader()
                    logger.debug('return')
                    return
        except futures._base.TimeoutError:
            # if didn't get at least half of votes in the alloted time
            pass
        # turn into a follower and reset state
        logger.info("Votes received")
        logger.debug("Candidate to follower")
        self._become_follower()

    def _whoami(self):
        """
        String representation of node's state.
        """
        if self.state == ServerStates.FOLLOWER:
            return 'FOLLOWER'
        elif self.state == ServerStates.CANDIDATE:
            return 'CANDIDATE'
        elif self.state == ServerStates.LEADER:
            return 'LEADER'

    def _set_voted_for(self, server_id):
        """
        Set the 'voted_for' variable and log it.
        """
        self.voted_for = server_id
        logger.info(f"Voted for node {server_id}")

    def _election_timeout_loop(self):
        """
        A loop which checks for timeouts and runs elections. Should be run in a separate thread
        """
        # Don't start until server is started
        self.run_event.wait()
        while self.run_event.is_set():
            # sleep while you still in time
            time.sleep(max(0.0, self.election_timeout - (time.monotonic() - self.previous_reset_time)))
            # if didn't receive messages for longer than specified timeout,
            # (note that a message can come while you were sleeping, so you still need to check for timeout)
            # you are a follower and not suspended
            if time.monotonic() - self.previous_reset_time > self.election_timeout and \
                    self.state == ServerStates.FOLLOWER and \
                    not self.is_suspended:
                self.mutex.acquire()
                logger.debug(f"{self.election_timeout}")
                # if this node is a follower - become candidate and start election
                logger.info(f"The leader is dead.")
                logger.debug(f"Follower to candidate, term: {self.term}")

                self._become_candidate()
                # start new election
                self._start_election()
                logger.debug(f"Time left: {time.monotonic() - self.previous_reset_time}")

                self.mutex.release()

    def _create_append_entry_request(self, address):
        # If there are unsent logs
        if self._prev_log_index(len(self.log_entries)) > self.next_index[address]:
            log_to_send = self.log_entries[self.next_index[address]]
        else:
            log_to_send = None
        # logs_to_send = items_at_indices(self.log_entries, self.next_index[address])

        append_entry_request = pb2.AppendEntryRequest(term=self.term,
                                                      leader_id=self.server_id,
                                                      prev_log_index=self._prev_log_index(self.next_index[address]),
                                                      prev_log_term=self._prev_log_term(self.next_index[address]),
                                                      log_entry=log_to_send,
                                                      leader_commit_index=self.commit_index,
                                                      has_entry=log_to_send is not None)

        return append_entry_request

    def _collect_heartbeat_replies(self, replies):
        for success, reply_term, address in replies:
            # If leader receives a term number that is greater than its own - turn into a follower
            if not success or reply_term > self.term:
                logger.debug("Process heartbeat replies; if")
                self.term = reply_term
                logger.debug("become follower in heartbeat")
                self._become_follower()
                break
            else:
                logger.debug(f"Process heartbeat replies; else {self.next_index[address]}, "
                             f"{self._prev_log_index(len(self.log_entries))}")
                if self._prev_log_index(len(self.log_entries)) != 0 \
                        and self.next_index[address] < self._prev_log_index(len(self.log_entries)):
                    self.next_index[address] += 1
                    self.match_index[address] += 1

    def _commit_approved_by_majority(self) -> None:
        sorted_match_indices = sorted(self.match_index.values())
        logger.debug(f'{sorted_match_indices}')
        # If number of other servers is even - mid should point to left border of the middle
        # If number of other servers is odd - mid should point to the right border of the middle
        mid = len(self.match_index) // 2 - (1 - len(self.match_index) % 2)
        next_commit = sorted_match_indices[mid]
        logger.debug(f'mid: {mid}, next_commit: {next_commit}')
        if next_commit > self.commit_index and self.log_entries[next_commit - 1].term == self.term:
            logger.debug(f"Committed new index: {next_commit}")
            for i in range(self.commit_index + 1, next_commit + 1):
                self.committed_events[i].set()
            self.commit_index = next_commit

    def _send_heartbeat_to(self, address):
        """
        This function sends a heartbeat to 'address' and processes the result, catches errors from malfunctioning
        servers.

        :param address: address of a node to which a heartbeat should be sent.
        """
        try:
            logger.debug(f'Sending heartbeat message to {address}')
            request = self._create_append_entry_request(address)
            logger.debug(f'Created request: {request}')
            reply = self.stubs[address].append_entries(request, timeout=self.heartbeat_interval)
            logger.debug(f'Sent heartbeat message to {address}')
            logger.debug(str(reply))

            return reply.success, reply.term, address
        except grpc._channel._InactiveRpcError:
            logger.debug('loh')
            return True, 0, address
        except grpc.RpcError as e:
            logger.debug('dksjflsekj')
            logger.debug(str(e))
            return True, 0, address

    def _heartbeat_if_leader(self):
        """
        A function that sends heartbeat messages if this node is a leader. Should run in a separate thread.
        """
        # Don't start until server is started
        self.run_event.wait()
        while self.run_event.is_set():
            # wait until you can start to send heartbeats
            self._send_heartbeats_flag.wait(timeout=1.0)
            # If server is a Leader
            if self.state == ServerStates.LEADER and not self.is_suspended:
                self.mutex.acquire()

                # Send messages to other nodes
                replies = self.pool.map(self._send_heartbeat_to, self.other_addresses)
                # Collect replies and check for errors
                self._collect_heartbeat_replies(replies)
                # Check whether server needs to commit an entry
                self._commit_approved_by_majority()

                # Every 'heartbeat interval' seconds
                self.mutex.release()
                time.sleep(self.heartbeat_interval)

    def _process_heartbeat(self, request, _):
        # if heartbeat came with term number greater than its own - turn into a follower
        if self.term < request.term:
            self.term = request.term
            self.leader_id = request.leader_id
            self._become_follower()
            return True
        # if the same term - just acknowledge the heartbeat
        else:
            self.leader_id = request.leader_id
            return True

    def _process_logs(self, request, _) -> bool:
        # Check that log at the index specified in the request contains the same term number.
        # If no, then there is inconsistency in logs and log at that index (and all consequent) should be deleted.
        logger.debug(f"In process logs. Request: {request}")
        if len(self.log_entries) != 0 and request.prev_log_index > 0 \
                and self.log_entries[request.prev_log_index - 1].term != request.term:
            logger.debug(f"Log entry. Terms are not equal: {self.log_entries[request.prev_log_index - 1].term}, "
                         f"{request.term}")
            self.log_entries = self.log_entries[:request.prev_log_index - 1]

        logger.debug(f"{request.prev_log_index}, {self._prev_log_index(len(self.log_entries))};"
                     f"{request.prev_log_term}, {self._prev_log_term(len(self.log_entries))}")
        if request.prev_log_index == self._prev_log_index(len(self.log_entries)) \
                and request.prev_log_term == self._prev_log_term(len(self.log_entries)):
            self.log_entries.append(request.log_entry)
            # success = self._append_log_entries(request.entries, request.leader_commit_index)
            return True
        else:
            return False

    def append_entries(self, request, context):
        """
        Function that receives heartbeat messages.
        """

        self.mutex.acquire()
        # update time of last received message and its type
        self.previous_reset_time = time.monotonic()
        self.last_received_message_type = 'append_entries'

        # if this node is suspended - return an error
        if self.is_suspended:
            logger.debug("return error")
            self.mutex.release()
            context.abort(grpc.StatusCode.UNAVAILABLE, 'I am suspended.')

        # If request comes from server with lower term number -
        # it is an outdated leader, return False.
        if request.term < self.term:
            self.mutex.release()
            return pb2.AppendEntryReply(term=self.term, success=False)

        # First, process the request as heartbeat
        heartbeats_reply = self._process_heartbeat(request, context)
        # Then, if the request carries a log - process the log
        if request.has_entry:
            logs_reply = self._process_logs(request, context)
        else:
            logs_reply = True

        # Set commit_index the same as leader's
        self.commit_index = request.leader_commit_index

        self.mutex.release()

        logger.debug(f"In append entries. Replies: {heartbeats_reply}, {logs_reply}.")

        return pb2.AppendEntryReply(term=self.term, success=heartbeats_reply and logs_reply)

    def request_vote(self, request, context):
        """
        Function that handles requests for votes from candidates.
        """
        self.mutex.acquire()
        # if this node is suspended - return an error
        if self.is_suspended:
            logger.debug("return error")
            self.mutex.release()
            context.abort(grpc.StatusCode.UNAVAILABLE, 'I am suspended.')
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
            logger.debug("become follower in request_vote")
            self._become_follower()

            self._set_voted_for(request.candidate_id)

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

        logger.info("Command from client: getleader")

        # if this node is a leader
        if self.state == ServerStates.LEADER:
            reply = pb2.GetLeaderReply(leader=pb2.GetLeaderPosAnswer(
                leader_id=self.server_id,
                leader_address=self.servers_info[self.server_id]
            ))
        # if there is a living leader in the system
        elif self.last_received_message_type == 'append_entries':
            reply = pb2.GetLeaderReply(leader=pb2.GetLeaderPosAnswer(
                leader_id=self.leader_id,
                leader_address=self.servers_info[self.leader_id]
            ))
        # That would mean that previous leader has died, so election is in progress
        elif self.last_received_message_type == 'request_vote':
            reply = pb2.GetLeaderReply(leader=pb2.GetLeaderPosAnswer(
                leader_id=self.voted_for,
                leader_address=self.servers_info[self.voted_for]
            ))
        else:
            reply = pb2.GetLeaderReply(empty_message=pb2.EmptyMessage())

        # if you send a positive reply - log its contents
        if hasattr(reply, 'leader'):
            logger.info(f'{reply.leader.leader_id} {reply.leader.leader_address}')
        else:
            logger.info("No leader.")

        return reply

    def shutdown(self):
        """
        Make a graceful shutdown of the server
        """
        self.run_event.clear()
        self.pool.shutdown()

    def _reset(self):
        """
        Reset server state
        """
        self.term = 0
        self.leader_id = None
        logger.debug("become follower in reset")
        self._become_follower()

    def suspend(self, request, context):
        """
        Suspend server for some time. After that server resets its state as if it was just started.
        """
        logger.info(f"Command from client: suspend {request.period}")
        self.is_suspended = True
        logger.info(f"Sleeping for {request.period} seconds")
        time.sleep(request.period)
        self._reset()
        self.is_suspended = False

        return pb2.EmptyMessage()

    def _broadcast_request(self, request_function):
        def helper(address: str):
            try:
                logger.debug(f'Sending heartbeat message to {address}')
                reply = request_function(self.stubs[address])
                logger.debug(f'Sent heartbeat message to {address}')
                logger.debug(str(reply))

                return reply
            except grpc._channel._InactiveRpcError or grpc.RpcError as e:
                logger.info(str(e))
                return

        return self.pool.map(helper, self.other_addresses)

    def _prev_log_index(self, index):
        return self.log_entries[index - 1].index if index > 0 else 0

    def _prev_log_term(self, index):
        return self.log_entries[index - 1].term if index > 0 else 0

    # def _notify_followers_about_log(self, log_requests):
    #     append_entry_request = pb2.AppendEntryRequest(term=self.term,
    #                                                   leader_id=self.leader_id,
    #                                                   prev_log_index=self._prev_log_index(),
    #                                                   prev_log_term=self._prev_log_term(),
    #                                                   entries=log_requests,
    #                                                   leader_commit_index=self.commit_index)
    #
    #     return self._broadcast_request(lambda stub: stub.append_entries(append_entry_request))

    def _commit_if_majority_acknowledged(self, replies):
        num_pos_acks = 0
        for reply in replies:
            num_pos_acks += int(reply.success)

            if num_pos_acks == len(self.other_addresses) // 2:
                self.leader_commit_index = len(self.log_entries)
                break

    def setval(self, request, context):
        if self.state == ServerStates.FOLLOWER:
            # If this is a follower - redirect the request to the leader
            return self.stubs[self.servers_info[self.leader_id]].setval(request)
        elif self.state == ServerStates.CANDIDATE:
            # If this is a candidate - return negative reply. It cannot do anything yet.
            # TODO: block until a leader is elected
            return pb2.SetValReply(is_success=False)
        elif self.state == ServerStates.LEADER:
            # Append new log to list of logs.
            index = self._prev_log_index(len(self.log_entries)) + 1
            self.log_entries.append(pb2.LogEntry(index=index,
                                                 term=self.term,
                                                 log=f"{request.key}={request.value}"
                                                 ))

            # Wait until log is replicated and committed.
            print('before wait')
            self.committed_events[index] = Event()
            self.committed_events[index].wait()
            print('after wait')

            return pb2.SetValReply(is_success=True)
        else:
            raise Exception("Unexpected state.")

    def getval(self, request, context):
        logger.info(f'{self.log_entries}')
        for log_entry in self.log_entries:
            if '=' in log_entry.log:
                key, value = log_entry.log.split('=')
                if key == request.key:
                    return pb2.GetValReply(value=value, is_success=True)
        else:
            return pb2.GetValReply(value='', is_success=False)


def which_address(config_path, server_id):
    """
    Print address of server 'server_id'.
    """
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
