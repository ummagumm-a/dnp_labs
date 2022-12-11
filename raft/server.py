from collections import namedtuple
import random
from typing import Iterator
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
import enum

# setup logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(message)s")
# log to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)


class ServerStates(enum.Enum):
    """
    Server can be in one of these states.
    """
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


LogEntry = namedtuple("LogEntry", ['index', 'term', 'log'])
SavedStub = namedtuple("SavedStub", ['channel', 'stub'])


class Server(pb2_grpc.RaftServicer):
    def __init__(self, server_id: int, config_path: str):
        start_time = time.monotonic()
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
        for _ in range(len(self.servers_info) - 1):
            thread_pool.submit(lambda: time.sleep(0.5))
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

        # A client can suspend nodes from the outside. If set to true, the server becomes not responsive.
        self.is_suspended = False
        # Time period between heartbeats sent by a leader
        self.heartbeat_interval = 0.05

        # Logs. Each entry is of the form: (index, term_number, command)
        self.log_entries = []
        self.commit_index = 0
        self.next_index = {address: len(self.log_entries) + 1 for address in self.other_addresses}
        self.match_index = {address: 0 for address in self.other_addresses}
        self.committed_events = {}

        logger.info(f"I am a {self._whoami()}. Term: {self.term}")

        # server runs until this variable is 'unset'. Required for graceful shutdown of the server
        self.run_event = Event()
        self.run_event.set()
        # The time of last received message. Required for timeout detection.
        self.previous_reset_time = time.monotonic()
        # Run thread which checks for timeout and runs elections
        self.election_loop_thread_handler = Timer(5, self._election_timeout_loop)
        self.election_loop_thread_handler.start()

        # Run thread which sends heartbeats if this node is a leader
        self._send_heartbeats_flag = Event()
        self._send_heartbeats_flag.clear()
        self.heartbeat_if_leader_thread_handler = Timer(5, self._heartbeat_if_leader)
        self.heartbeat_if_leader_thread_handler.start()

        logger.debug(f'Initialization time: {time.monotonic() - start_time}')

    def _reset_election_timeout(self):
        self.election_timeout = random.uniform(0.15, 0.3)

    def _make_stubs(self):
        """
        Create stubs to all other nodes in the system.
        """

        def helper(address: str) -> SavedStub:
            channel = grpc.insecure_channel(address)
            stub = pb2_grpc.RaftStub(channel)
            return SavedStub(channel, stub)

        stubs = {address: helper(address)
                 for address in self.other_addresses}
        return stubs

    def _send_request_for_vote(self, address):
        """
        Send a request for vote to a node located at 'address'.
        """
        try:
            request = pb2.RequestVoteRequest(term=self.term, candidate_id=self.server_id,
                                             last_log_index=self.log_entries[-1].index
                                                            if len(self.log_entries) > 0 else 0,
                                             last_log_term=self.log_entries[-1].term
                                                           if len(self.log_entries) > 0 else 0)
            reply = self.stubs[address].stub.request_vote(request)
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
        self.previous_reset_time = time.monotonic()
        logger.info(f"I am a {self._whoami()}. Term: {self.term}")
        # vote for yourself
        self._set_voted_for(self.server_id)

    def _become_leader(self):
        """
        Turn into a leader and update state accordingly.
        """
        self.previous_reset_time = time.monotonic()
        self.next_index = {address: len(self.log_entries) + 1 for address in self.other_addresses}
        self.match_index = {address: 0 for address in self.other_addresses}
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
                    # self.term = term
                    # self.term -= 1
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
        logger.debug(f"Election timeout loop started: {time.monotonic() - self.previous_reset_time}")
        self.previous_reset_time = time.monotonic()
        while self.run_event.is_set():
            # sleep while you still in time
            time.sleep(max(0.0, self.election_timeout - (time.monotonic() - self.previous_reset_time)))
            # if didn't receive messages for longer than specified timeout,
            # (note that a message can come while you were sleeping, so you still need to check for timeout)
            # you are a follower and not suspended
            if time.monotonic() - self.previous_reset_time > self.election_timeout and \
                    self.state == ServerStates.FOLLOWER and \
                    not self.is_suspended:
                logger.debug("Inside election loop if")
                with self.mutex:
                    logger.debug(f"{self.election_timeout}")
                    # if this node is a follower - become candidate and start election
                    logger.info(f"The leader is dead.")
                    logger.debug(f"Follower to candidate, term: {self.term}")

                    self._become_candidate()
                    # start new election
                    self._start_election()
                    logger.debug(f"Time left: {time.monotonic() - self.previous_reset_time}")

    def _create_append_entry_request(self, address: str) -> pb2.AppendEntryRequest:
        """
        Creates append entry request with all required fields.

        :param address: address to a node to which the request will be sent.
        """
        logger.debug(f"create append entry request {self._prev_log_index(len(self.log_entries))} "
                     f"{self.next_index[address]} {self.match_index[address]}")

        # If the leader needs to send some logs to node at this address
        if len(self.log_entries) >= self.next_index[address]:
            log_to_send = self.log_entries[self.next_index[address] - 1]
            prev_log_index = self.next_index[address] - 1
            prev_log_term = self.log_entries[self.next_index[address] - 2].term if self.next_index[address] >= 2 else 0
        else:
            # Otherwise, it is just a heartbeat, and it fills these fields with default values.
            log_to_send = None
            prev_log_index = 0
            prev_log_term = 0

        append_entry_request = pb2.AppendEntryRequest(term=self.term,
                                                      leader_id=self.server_id,
                                                      prev_log_index=prev_log_index,
                                                      prev_log_term=prev_log_term,
                                                      log_entry=log_to_send,
                                                      leader_commit_index=self.commit_index,
                                                      has_entry=log_to_send is not None)

        return append_entry_request

    def _collect_heartbeat_replies(self, replies: Iterator[tuple[bool, int, str]]) -> None:
        """
        Collects replies for heartbeats from other nodes, check whether it was a success, updates its state accordingly
        """
        for success, reply_term, address in replies:
            # That would indicate that there are problems with other server
            # which have nothing to do with heartbeats or logs,
            # i.e. it is inaccessible or has an error.
            if not success and reply_term == -1:
                continue
            # If leader receives a term number that is greater than its own - turn into a follower
            if reply_term > self.term:
                logger.debug("Process heartbeat replies; if")
                self.term = reply_term
                logger.debug("become follower in heartbeat")
                self._become_follower()
                break
            else:
                logger.debug(f"Process heartbeat replies; else {self.next_index[address]}, "
                             f"{self._prev_log_index(len(self.log_entries))}")
                # If you sent logs in this heartbeat interval.
                if len(self.log_entries) >= self.next_index[address]:
                    # If sent this log successfully - update match_index and increment next_index.
                    if success:
                        logger.debug("Reply success")
                        self.match_index[address] = self.next_index[address]
                        self.next_index[address] += 1
                    # Otherwise, there is log inconsistency and leader should try to send an earlier log.
                    else:
                        logger.debug("Reply not success")
                        self.next_index[address] -= 1

    def _commit_approved_by_majority(self) -> None:
        """
        Check for logs which are acknowledged by majority but are not yet committed.
        """
        sorted_match_indices = sorted(self.match_index.values())
        logger.debug(f'{sorted_match_indices}')
        mid = len(self.match_index) // 2
        # This will be the index of the greatest log acknowledged by majority
        next_commit = sorted_match_indices[mid]
        logger.debug(f'mid: {mid}, next_commit: {next_commit}, self.commit_index: {self.commit_index}')
        # If this log is not committed and was sent out in the current term.
        if next_commit > self.commit_index and self.log_entries[next_commit - 1].term == self.term:
            logger.debug(f"Committed new index: {next_commit}")
            # Allow to send a positive result to the client
            for i in range(self.commit_index + 1, next_commit + 1):
                self.committed_events[i].set()
            self.commit_index = next_commit

    def _send_heartbeat_to(self, address: str) -> (bool, int, str):
        """
        This function sends a heartbeat to 'address' and processes the result, catches errors from malfunctioning
        servers.

        :param address: address of a node to which a heartbeat should be sent.
        :returns: whether reply indicates a success, receiver's term and address (same as input)
                  success False and term -1 indicates that there were some problems while sending the request.
        """

        logger.debug(f'Sending heartbeat message to {address}')
        # Create request specifically for node at this address
        request = self._create_append_entry_request(address)
        logger.debug(f'Created request: {request}')
        # TODO: check timeout. Problem with starting servers may be here.
        start_time = time.monotonic()
        try:
            logger.debug(f"Connectivity to {address} "
                         f"is {self.stubs[address].channel._connectivity_state.connectivity}")
            # Check that this node is up and ready to accept requests
            grpc.channel_ready_future(self.stubs[address].channel).result(self.heartbeat_interval)

            reply = self.stubs[address].stub.append_entries(request, self.heartbeat_interval)
            logger.debug(f'Sent heartbeat message to {address}, {time.monotonic() - start_time}')
            logger.debug(str(reply))

            return reply.success, reply.term, address
        except grpc.FutureTimeoutError:
            # In case node is not ready to accept requests
            logger.debug(f"Channel {address} is not ready.")

            return False, -1, address
        except grpc.RpcError as e:
            logger.debug("Other node's error while sending heartbeat")
            logger.debug(str(e))
            return False, -1, address

    def _heartbeat_if_leader(self) -> None:
        """
        A function that sends heartbeat messages if this node is a leader. Should run in a separate thread.
        Sends out all not yet replicated logs.
        """
        # Don't start until server is started
        # self.run_event.wait()
        logger.debug(f"heartbeat thread started: {time.monotonic() - self.previous_reset_time}")
        while self.run_event.is_set():
            # wait until you can start to send heartbeats
            self._send_heartbeats_flag.wait(timeout=1.0)

            start_time = time.monotonic()
            # If server is a Leader
            if self.state == ServerStates.LEADER and not self.is_suspended:
                logger.debug('inside heartbeat if')
                logger.debug(str(self.next_index))
                logger.debug(str(self.match_index))
                logger.debug(f'{self.log_entries}')
                start_time = time.monotonic()
                with self.mutex:
                    # Send messages to other nodes
                    replies = self.pool.map(self._send_heartbeat_to, self.other_addresses)
                    # Collect replies and check for errors
                    self._collect_heartbeat_replies(replies)
                    # Check whether server needs to commit an entry
                    self._commit_approved_by_majority()

                # Every 'heartbeat interval' seconds
                time.sleep(max(0.0, self.heartbeat_interval - (time.monotonic() - start_time)))

            logger.debug(f'heartbeat time: {time.monotonic() - start_time}')

    def _process_heartbeat(self, request: pb2.AppendEntryRequest, _):
        """
        Process incoming append_entries request as heartbeat.
        """
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

    def _process_logs(self, request: pb2.AppendEntryRequest, _) -> bool:
        """
        Accept logs from incoming request

        :returns: whether accepted logs successfully.
        """
        logger.debug(f"process logs. Request: {request}. ")
        logger.debug(f"{len(self.log_entries)} {request.prev_log_index - 1}")
        logger.debug(f"{len(self.log_entries)} {request.prev_log_index}")
        if len(self.log_entries) > request.prev_log_index - 1 and request.prev_log_index != 0:
            logger.debug("1")
            logger.debug(f"{self.log_entries[request.prev_log_index - 1].term} ")
        if len(self.log_entries) > request.prev_log_index:
            logger.debug("2")
            logger.debug(f"{self.log_entries[request.prev_log_index].term}")

        # If there are fewer logs than indicated in prev_log_index - previous log physically cannot be present.
        # or log at prev_log_index has term mismatch with the new log
        if len(self.log_entries) <= request.prev_log_index - 1 \
                or (len(self.log_entries) > request.prev_log_index - 1
                    and request.prev_log_index != 0
                    and self.log_entries[request.prev_log_index - 1].term != request.prev_log_term):
            return False
        logger.debug('pp')

        # If log at index specified in new log has a term mismatch with the new log -
        # remove its log and all subsequent ones
        if len(self.log_entries) > request.prev_log_index \
                and self.log_entries[request.prev_log_index].term != request.term:
            self.log_entries = self.log_entries[:request.prev_log_index]

        # Append new log to the list
        self.log_entries.append(request.log_entry)
        logger.debug(f"Logs now: {self.log_entries}")

        return True

    def append_entries(self, request: pb2.AppendEntryRequest, context) -> pb2.AppendEntryReply:
        """
        Function that receives heartbeat messages and accepts new logs.
        """

        # logger.debug(f"beg append_entries, {time.monotonic() - self.previous_reset_time}.")
        with self.mutex:
            # update time of last received message and its type
            self.previous_reset_time = time.monotonic()
            self.last_received_message_type = 'append_entries'
            # logger.debug("append_entries")

            # if this node is suspended - return an error
            if self.is_suspended:
                logger.debug("return error")
                context.abort(grpc.StatusCode.UNAVAILABLE, 'I am suspended.')

            # If request comes from server with lower term number -
            # it is an outdated leader, return False.
            if request.term < self.term:
                return pb2.AppendEntryReply(term=self.term, success=False)

            # First, process the request as heartbeat
            heartbeats_reply = self._process_heartbeat(request, context)
            # Then, if the request carries a log - process the log
            if request.has_entry:
                logger.debug('append entry has entry')
                logs_reply = self._process_logs(request, context)
            else:
                logs_reply = True

            # Set commit_index the same as leader's
            if request.leader_commit_index > self.commit_index:
                logger.debug(f"Update commit index. "
                             f"Old: {self.commit_index}. "
                             f"New:{request.leader_commit_index} "
                             f"or {self.log_entries[-1].index if len(self.log_entries) > 0 else 0}")
                self.commit_index = min(request.leader_commit_index,
                                        self.log_entries[-1].index if len(self.log_entries) > 0 else 0)

            if not (heartbeats_reply and logs_reply):
                logger.debug(f"In append entries. Replies: {heartbeats_reply}, {logs_reply}.")

            return pb2.AppendEntryReply(term=self.term, success=heartbeats_reply and logs_reply)

    def request_vote(self, request: pb2.RequestVoteRequest, context) -> pb2.RequestVoteReply:
        """
        Function that handles requests for votes from candidates.
        """
        logger.debug('request vote beg')
        with self.mutex:
            # if this node is suspended - return an error
            if self.is_suspended:
                logger.debug("return error")
                context.abort(grpc.StatusCode.UNAVAILABLE, 'I am suspended.')

            logger.debug("request_vote")
            logger.debug(str(request))
            # update timer because a new message is received
            self.previous_reset_time = time.monotonic()
            logger.debug("lkejrls")
            self.last_received_message_type = 'request_vote'

            logger.debug('sldkfjwoel')
            logger.debug(f"Request vote {request.last_log_index} {len(self.log_entries)}")
            # if term of candidate is greater
            if self.term < request.term and request.last_log_index >= len(self.log_entries):
                # update your own term
                self.term = request.term
                # vote for this candidate
                self._set_voted_for(request.candidate_id)
                # server becomes a follower
                logger.debug("become follower in request_vote")
                self._become_follower()

                # send positive answer
                reply = pb2.RequestVoteReply(term=self.term, result=True)

            # if server and candidate are in the same term and server didn't yet vote for anyone in this term
            # and log of the candidate is at least as up-to-date as this node's log.
            elif self.term == request.term and self.voted_for is None and self.state != ServerStates.LEADER \
                    and request.last_log_index >= len(self.log_entries):
                # server saves info that it voted for this candidate
                self._set_voted_for(request.candidate_id)

                # send positive answer
                reply = pb2.RequestVoteReply(term=self.term, result=True)
            else:
                # send negative answer
                reply = pb2.RequestVoteReply(term=self.term, result=False)

            return reply

    def get_leader(self, request: pb2.EmptyMessage, context) -> pb2.GetLeaderReply:
        """
        Returns the current leader in the system.
        If leader is alive - send id and address of this leader.
        If election is in progress - send id and address of the node that this node voted for.
        If node didn't vote in this term yet - return nothing.
        """

        logger.info(f"Command from client: getleader {time.monotonic() - self.previous_reset_time}")

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

    def _prev_log_index(self, index: int) -> int:
        """
        Returns index of log right before the one at 'index'.
        If 'index' is 0, i.e. points to the first element - send 0 as indication that there are no previous logs.
        """
        return self.log_entries[index - 1].index if index > 0 else 0

    def setval(self, request: pb2.Log, context) -> pb2.SetValReply:
        """
        Accept a new log and replicate it over all nodes. This function is called by the client.
        """
        if self.state == ServerStates.FOLLOWER:
            # If this is a follower - redirect the request to the leader
            logger.debug(
                f"Redirecting request {request} to leader {self.leader_id} at address {self.servers_info[self.leader_id]}.")
            return self.stubs[self.servers_info[self.leader_id]].stub.setval(request)
        elif self.state == ServerStates.CANDIDATE:
            # If this is a candidate - return negative reply. It cannot do anything yet.
            # TODO: block until a leader is elected
            return pb2.SetValReply(is_success=False)
        elif self.state == ServerStates.LEADER:
            with self.mutex:
                # Append new log to list of logs.
                index = self._prev_log_index(len(self.log_entries)) + 1
                self.log_entries.append(pb2.LogEntry(index=index,
                                                     term=self.term,
                                                     log=f"{request.key}={request.value}"
                                                     ))

                # Wait until log is replicated and committed.
                logger.debug('before wait')
                self.committed_events[index] = Event()
            self.committed_events[index].wait()
            # TODO: added just now
            del self.committed_events[index]
            logger.debug('after wait')

            return pb2.SetValReply(is_success=True)
        else:
            raise Exception("Unexpected state.")

    def getval(self, request: pb2.GetValRequest, context) -> pb2.GetValReply:
        """
        Get value with key specified in request. This function is called by the client.
        """
        logger.debug(f'{self.log_entries}')

        # Start searching from the latest committed log and to the bottom of the list.
        # This is required in case there are several logs with the same key. We need to return the latest one.
        for i in range(self.commit_index - 1, -1, -1):
            if '=' in self.log_entries[i].log:
                key, value = self.log_entries[i].log.split('=')
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
    import cProfile

    with cProfile.Profile() as pr:
        config_path = 'config.conf'
        server_id = int(sys.argv[1])
        # Print the address of this server
        server_address = which_address(config_path, server_id)
        thread_pool = futures.ThreadPoolExecutor(max_workers=20)
        for i in range(10):
            thread_pool.submit(lambda: time.sleep(0.5))

        # setup and run server
        grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        server = Server(server_id, config_path)
        try:
            t1 = time.monotonic()
            pb2_grpc.add_RaftServicer_to_server(server, grpc_server)
            t2 = time.monotonic()
            logger.debug(t2 - t1)
            grpc_server.add_insecure_port(server_address)
            t3 = time.monotonic()
            logger.debug(t3 - t2)

            t4 = time.monotonic()
            grpc_server.start()
            logger.debug(t4 - t3)
            grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("Shutdown...")
            server.shutdown()
            grpc_server.stop(3)

        # import pstats
        # ps = pstats.Stats(pr).sort_stats('cumtime')
        # ps.print_stats()
