import unittest
import solution
from custom_maps import MAPS
from validation import validate_solution


class CustomMapTests(unittest.TestCase):
    def test_all_maps(self):
        for name, state, expected in MAPS:
            with self.subTest(map=name):
                final = solution.solve(state, timebound=20)
                if expected is None:
                    self.assertIs(final, False)
                else:
                    valid, msg = validate_solution(state, final)
                    self.assertTrue(valid, msg)
                    self.assertEqual(final.gval, expected)


if __name__ == "__main__":
    unittest.main()