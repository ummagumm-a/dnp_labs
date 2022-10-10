import unittest
from utils import get_succ, get_pred, ring_between


class UtilsTest(unittest.TestCase):
    def test_get_succ(self):
        other_ids = [2, 12, 20]

        self.assertEqual(get_succ(5, other_ids), 12)
        self.assertEqual(get_succ(21, other_ids), 2)
        self.assertEqual(get_succ(1, other_ids), 2)
        
    def test_get_pred(self):
        other_ids = [2, 12, 20]

        self.assertEqual(get_pred(5, other_ids), 2)
        self.assertEqual(get_pred(21, other_ids), 20)
        self.assertEqual(get_pred(1, other_ids), 20)

    def test_ring_between(self):
        self.assertTrue(ring_between(16, 17, 18))
        self.assertFalse(ring_between(17, 16, 18))
        self.assertFalse(ring_between(18, 17, 16))
        self.assertTrue(ring_between(17, 18, 16))
        self.assertFalse(ring_between(16, 18, 17))
        self.assertTrue(ring_between(18, 16, 17))
        self.assertTrue(ring_between(16, 17, 16))

if __name__ == '__main__':
    unittest.main()