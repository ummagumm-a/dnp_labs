import unittest
from server import Server, ServerStates
import time


class ServerElectionTimeoutTest(unittest.TestCase):
    def election_timeout_loop_test(self):
        server = Server(1, 'config.conf')
        self.assertEqual(server.state, ServerStates.FOLLOWER)
        time.sleep(0.05)
        self.assertEqual(server.state, ServerStates.FOLLOWER)
        time.sleep(0.05)
        self.assertEqual(server.state, ServerStates.FOLLOWER)
        time.sleep(0.21)
        self.assertEqual(server.state, ServerStates.CANDIDATE)

        server.shutdown()


if __name__ == '__main__':
    unittest.main()
