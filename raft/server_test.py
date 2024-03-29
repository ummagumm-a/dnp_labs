import unittest
from server import Server, ServerStates
import time
import raft_pb2 as pb2


class ElectionTimeoutTest(unittest.TestCase):

    def test_election_timeout_loop(self):
        self.server = Server(1, 'config.conf')
        print(self.server.election_timeout)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        print(time.monotonic() - self.server.previous_reset_time, time.monotonic(), self.server.previous_reset_time)
        time.sleep(0.01)
        print(time.monotonic() - self.server.previous_reset_time, time.monotonic(), self.server.previous_reset_time)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        time.sleep(0.31)
        print(time.monotonic() - self.server.previous_reset_time, time.monotonic(), self.server.previous_reset_time)
        self.assertEqual(self.server.state, ServerStates.CANDIDATE)
        self.assertEqual(self.server.term, 1)
        self.assertEqual(self.server.voted_for, 1)

    def tearDown(self) -> None:
        self.server.shutdown()


class RequestVoteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.server = Server(1, 'config.conf')

    def tearDown(self) -> None:
        self.server.shutdown()

    def test_request_vote_timer_update(self):
        timer1 = self.server.previous_reset_time
        request = pb2.RequestVoteRequest(term=0, candidate_id=2)
        _ = self.server.request_vote(request, None)
        self.assertNotAlmostEqual(timer1, self.server.previous_reset_time)

    def test_request_vote_same_term_follower_did_not_vote(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.FOLLOWER
        self.server.voted_for = None

        request = pb2.RequestVoteRequest(term=term, candidate_id=2)
        reply = self.server.request_vote(request, None)

        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=True))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.voted_for, 2)
        self.assertEqual(self.server.term, term)

    def test_request_vote_same_term_follower_did_vote(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.FOLLOWER
        self.server.voted_for = 3

        request = pb2.RequestVoteRequest(term=term, candidate_id=2)
        reply = self.server.request_vote(request, None)

        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.voted_for, 3)
        self.assertEqual(self.server.term, term)


    def test_request_vote_same_term_candidate(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.CANDIDATE
        self.server.voted_for = self.server.server_id

        request = pb2.RequestVoteRequest(term=term, candidate_id=2)
        reply = self.server.request_vote(request, None)

        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.CANDIDATE)
        self.assertEqual(self.server.voted_for, self.server.server_id)
        self.assertEqual(self.server.term, term)

    def test_request_vote_same_term_leader(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.LEADER
        self.server.voted_for = self.server.server_id

        request = pb2.RequestVoteRequest(term=term, candidate_id=2)
        reply = self.server.request_vote(request, None)
        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.LEADER)
        self.assertEqual(self.server.voted_for, self.server.server_id)
        self.assertEqual(self.server.term, term)

    def test_request_vote_greater_term_follower_did_not_vote(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.FOLLOWER
        self.server.voted_for = None

        request = pb2.RequestVoteRequest(term=term + 1, candidate_id=2)
        reply = self.server.request_vote(request, None)

        self.assertEqual(reply, pb2.RequestVoteReply(term=term + 1, result=True))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.voted_for, 2)
        self.assertEqual(self.server.term, term + 1)

    def test_request_vote_greater_term_follower_did_vote(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.FOLLOWER
        self.server.voted_for = 3

        request = pb2.RequestVoteRequest(term=term + 1, candidate_id=2)
        reply = self.server.request_vote(request, None)

        self.assertEqual(reply, pb2.RequestVoteReply(term=term + 1, result=True))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.voted_for, 2)
        self.assertEqual(self.server.term, term + 1)

    def test_request_vote_greater_term_candidate(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.CANDIDATE
        self.server.voted_for = self.server.server_id

        request = pb2.RequestVoteRequest(term=term + 1, candidate_id=2)
        reply = self.server.request_vote(request, None)

        self.assertEqual(reply, pb2.RequestVoteReply(term=term + 1, result=True))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.term, term + 1)
        self.assertEqual(self.server.voted_for, 2)

    def test_request_vote_greater_term_leader(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.LEADER
        self.server.voted_for = self.server.server_id

        request = pb2.RequestVoteRequest(term=term + 1, candidate_id=2)
        reply = self.server.request_vote(request, None)
        self.assertEqual(reply, pb2.RequestVoteReply(term=term + 1, result=True))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.term, term + 1)
        self.assertEqual(self.server.voted_for, 2)

    def test_request_vote_lower_term_leader(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.LEADER
        self.server.voted_for = self.server.server_id

        request = pb2.RequestVoteRequest(term=term - 1, candidate_id=2)
        reply = self.server.request_vote(request, None)
        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.LEADER)
        self.assertEqual(self.server.term, term)
        self.assertEqual(self.server.voted_for, self.server.server_id)

    def test_request_vote_lower_term_candidate(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.CANDIDATE
        self.server.voted_for = self.server.server_id

        request = pb2.RequestVoteRequest(term=term - 1, candidate_id=2)
        reply = self.server.request_vote(request, None)
        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.CANDIDATE)
        self.assertEqual(self.server.term, term)
        self.assertEqual(self.server.voted_for, self.server.server_id)

    def test_request_vote_lower_term_follower_did_not_vote(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.FOLLOWER
        self.server.voted_for = None

        request = pb2.RequestVoteRequest(term=term - 1, candidate_id=2)
        reply = self.server.request_vote(request, None)
        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.term, term)
        self.assertIsNone(self.server.voted_for)

    def test_request_vote_lower_term_follower_did_vote(self):
        term = 5
        self.server.term = term
        self.server.state = ServerStates.FOLLOWER
        self.server.voted_for = 3

        request = pb2.RequestVoteRequest(term=term - 1, candidate_id=2)
        reply = self.server.request_vote(request, None)
        self.assertEqual(reply, pb2.RequestVoteReply(term=term, result=False))
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertEqual(self.server.term, term)
        self.assertEqual(self.server.voted_for, 3)


class AppendEntriesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.server = Server(1, 'config.conf')

    def tearDown(self) -> None:
        self.server.shutdown()

    def test_same_term_follower(self):
        """
        If it is a follower and the term is the same - nothing should change (except of timer)
        """

        request = pb2.AppendEntryRequest(term=0, leader_id=2)
        self.server.append_entries(request, None)

        self.assertAlmostEqual(self.server.previous_reset_time, time.monotonic(), places=3)
        self.assertEqual(self.server.term, 0)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)

    def test_greater_term_follower(self):
        request = pb2.AppendEntryRequest(term=1, leader_id=2)
        self.server.append_entries(request, None)

        self.assertAlmostEqual(self.server.previous_reset_time, time.monotonic(), places=3)
        self.assertEqual(self.server.term, 1)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertIsNone(self.server.voted_for)

    def test_greater_term_leader(self):
        self.server.state = ServerStates.LEADER
        self.server.voted_for = self.server.server_id
        request = pb2.AppendEntryRequest(term=1, leader_id=2)
        self.server.append_entries(request, None)

        self.assertAlmostEqual(self.server.previous_reset_time, time.monotonic(), places=3)
        self.assertEqual(self.server.term, 1)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertIsNone(self.server.voted_for)

    def test_greater_term_candidate(self):
        self.server.state = ServerStates.CANDIDATE
        self.server.voted_for = self.server.server_id
        request = pb2.AppendEntryRequest(term=1, leader_id=2)
        self.server.append_entries(request, None)

        self.assertAlmostEqual(self.server.previous_reset_time, time.monotonic(), places=3)
        self.assertEqual(self.server.term, 1)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertIsNone(self.server.voted_for)

    def test_same_term_candidate(self):
        self.server.state = ServerStates.CANDIDATE
        self.server.voted_for = self.server.server_id
        request = pb2.AppendEntryRequest(term=0, leader_id=2)
        self.server.append_entries(request, None)

        self.assertAlmostEqual(self.server.previous_reset_time, time.monotonic(), places=3)
        self.assertEqual(self.server.term, 0)
        self.assertEqual(self.server.state, ServerStates.FOLLOWER)
        self.assertIsNone(self.server.voted_for)


if __name__ == '__main__':
    unittest.main()
