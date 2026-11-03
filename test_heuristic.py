import unittest
import solution
from custom_maps import MAPS, make
from sokoban import PROBLEMS, sokoban_goal_state
 
M = {name: state for name, state, _ in MAPS}
 
# Số bước tối ưu của map 0..8, lấy từ BFS baseline (độc lập với heuristic)
OPT = [16, 4, 21, 10, 8, 30, 16, 41, 14]
TB = 30  # giây
 
KHOI = [(2, 1), (3, 1), (2, 2), (3, 2)]
MAP_A = make(6, 5, [(0, 0)], KHOI, [(0, 4), (1, 4), (2, 4), (3, 4)])
MAP_B = make(6, 5, [(0, 0)], KHOI, KHOI)
MAP_C = make(6, 5, [(0, 0)], [(2, 1), (3, 1), (2, 2)], [(5, 0), (5, 1), (5, 2)])
MAP_D = make(6, 5, [(0, 0)], KHOI, [(2, 1), (3, 1), (2, 2), (0, 4)])


def duong_di(final):
    """Chuỗi trạng thái từ đầu đến final (đi ngược theo parent rồi đảo)."""
    p = []
    while final is not None:
        p.append(final)
        final = final.parent
    return p[::-1] 
 
 
def ket_2x2(state):
    """Gọi hàm phát hiện bế tắc 2x2 của B trên chính các thùng của state."""
    return solution.lam_ham_khoi_2x2(state)(state.boxes)
 

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
 
 
class TestBeTac2x2(unittest.TestCase):
    def test_phat_hien_khoi_2x2(self):
        self.assertTrue(ket_2x2(MAP_A))
        self.assertTrue(ket_2x2(MAP_D))
 
    def test_khong_loai_nham(self):
        self.assertFalse(ket_2x2(MAP_B))   # khối toàn thùng trên đích
        self.assertFalse(ket_2x2(MAP_C))   # còn ô trống
 
    def test_solve_tren_be_tac(self):
        self.assertIs(solution.solve(MAP_A, 10), False)
        self.assertIs(solution.solve(MAP_D, 10), False)
 
    def test_khong_cat_nham_loi_giai(self):
        self.assertIs(solution.solve(MAP_B, 10), MAP_B)
        final = solution.solve(MAP_C, 30)
        self.assertIsNot(final, False)
        self.assertEqual(final.gval, 18)   # BFS độc lập cho 18
 
    def test_tham_so_dung_2x2(self):
        # Tắt bộ phát hiện thì map A không còn bị coi là bế tắc: chứng tỏ INF đến từ detector
        h_tat, _ = solution.make_heuristics(MAP_A, dung_2x2=False)
        h_bat, _ = solution.make_heuristics(MAP_A, dung_2x2=True)
        self.assertLess(h_tat(MAP_A), solution.INF)
        self.assertGreaterEqual(h_bat(MAP_A), solution.INF)
 
 
class TestHaiHeuristic(unittest.TestCase):
    def test_tra_du_hai_ham(self):
        h_admissible, h_fast = solution.make_heuristics(MAP_C)
        self.assertTrue(callable(h_admissible))
        self.assertTrue(callable(h_fast))
 
    def test_h_admissible(self):
        h_adm, _ = solution.make_heuristics(MAP_C)
        self.assertLessEqual(h_adm(MAP_C), 18)          # không vượt chi phí tối ưu
        h_adm_a, _ = solution.make_heuristics(MAP_A)
        self.assertGreaterEqual(h_adm_a(MAP_A), solution.INF)   # loại trạng thái bế tắc
 
    def test_h_fast_huu_han_tren_duong_di(self):
        final = solution.solve(MAP_C, 30)
        _, h_fast = solution.make_heuristics(MAP_C)
        for s in duong_di(final):
            v = h_fast(s)
            self.assertGreaterEqual(v, 0)
            self.assertLess(v, solution.INF)
        # KHÔNG kiểm tra h_fast <= chi phí còn lại: h_fast có thể không admissible
    

    def test_h_fast_cong_khoang_di_bo(self):
        h_adm, h_fast = solution.make_heuristics(MAP_C)
        # Trên MAP_C, vị trí đứng gần nhất để đẩy một thùng cách robot 2 bước.
        self.assertEqual(h_fast(MAP_C) - h_adm(MAP_C), 2)


    def test_h_fast_khong_cong_khi_robot_da_sat_thung(self):
        st = make(6, 5, [(1, 1)], KHOI, [(5, 0), (5, 1), (5, 2)])
        h_adm, h_fast = solution.make_heuristics(st)
        # Robot đã ở vị trí có thể đẩy một thùng, nên ước lượng đi bộ bằng 0.
        self.assertEqual(h_fast(st), h_adm(st))


    def test_ghep_cap_h1_thap_hon_h2(self):
        st = M["dich_nhieu_hon_thung"]
        self.assertEqual(solution.make_heuristic(st)(st), 2)
        self.assertEqual(solution.make_heuristic_h2(st)(st), 3)
 
    def test_thung_da_o_dich_tinh_0(self):
        st = M["thung_da_o_dich"]
        self.assertEqual(solution.make_heuristic_h2(st)(st), 1)
 
 
class TestDocDuongToiUu(unittest.TestCase):
    def test_admissible_va_khong_bi_cat_nham(self):
        for i in range(9):  # các map A* giải nhanh
            with self.subTest(map=i):
                st = PROBLEMS[i]
                final = solution.solve(st, TB)
                self.assertIsNot(final, False, f"solve không giải được map {i} trong {TB}s")
                self.assertTrue(sokoban_goal_state(final))
                self.assertEqual(final.gval, OPT[i])  # đường đi thật sự tối ưu
                h_adm, _ = solution.make_heuristics(st)
                for s in duong_di(final):
                    con_lai = final.gval - s.gval
                    self.assertLessEqual(h_adm(s), con_lai)   # admissible
                    self.assertFalse(ket_2x2(s))              # không cắt nhầm trạng thái trên lời giải
 
 
if __name__ == "__main__":
    unittest.main()