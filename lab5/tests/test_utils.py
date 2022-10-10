import sys
print(sys.path)
import unittest
from utils import get_succ, get_pred


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

if __name__ == '__main__':
    unittest.main()