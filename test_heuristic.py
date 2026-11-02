import unittest
import solution
from custom_maps import MAPS
from sokoban import PROBLEMS, sokoban_goal_state

# Số bước tối ưu của map 0..8, lấy từ BFS baseline (độc lập với heuristic)
OPT = [16, 4, 21, 10, 8, 30, 16, 41, 14]
TB = 30  # giây


M = {name: state for name, state, _ in MAPS}


def duong_di(final):
    """Chuỗi trạng thái từ đầu đến final (đi ngược theo parent rồi đảo)."""
    p = []
    while final is not None:
        p.append(final)
        final = final.parent
    return p[::-1]


class TestOChet(unittest.TestCase):
    def test_map1_chi_2_o_song(self):
        _, dist_to_goal, dead = solution.tinh_bang(M["vo_nghiem_goc"])
        self.assertEqual(set(dist_to_goal), {(1, 1), (2, 1)})
        self.assertEqual(len(dead), 10)

    def test_map4_o_chet(self):
        _, _, dead = solution.tinh_bang(M["mot_robot_re_goc"])
        self.assertEqual(dead, {(0, 0), (0, 1), (0, 2), (0, 3),
                                (1, 0), (2, 0), (3, 0), (4, 0)})

    def test_map4_khoang_cach_day(self):
        _, d, _ = solution.tinh_bang(M["mot_robot_re_goc"])
        self.assertEqual([d[(1, 1)], d[(2, 1)], d[(4, 2)], d[(4, 3)]],
                         [5, 4, 1, 0])


class TestHeuristic(unittest.TestCase):
    def test_ghep_cap_h1_thap_hon_h2(self):
        st = M["dich_nhieu_hon_thung"]
        self.assertEqual(solution.make_heuristic(st)(st), 2)
        self.assertEqual(solution.make_heuristic_h2(st)(st), 3)

    def test_thung_da_o_dich_tinh_0(self):
        st = M["thung_da_o_dich"]
        self.assertEqual(solution.make_heuristic_h2(st)(st), 1)

    def test_admissible_doc_duong_di(self):
        for i in range(9):  # các map A* giải nhanh
            with self.subTest(map=i):
                st = PROBLEMS[i]
                final = solution.solve(st, TB)
                self.assertIsNot(final, False,
                                 f"solve không giải được map {i} trong {TB}s")
                self.assertTrue(sokoban_goal_state(final))
                self.assertEqual(final.gval, OPT[i])  # đường đi thật sự tối ưu
                h = solution.make_heuristic_h2(st)
                for s in duong_di(final):
                    con_lai = final.gval - s.gval
                    self.assertLessEqual(h(s), con_lai)


if __name__ == "__main__":
    unittest.main()