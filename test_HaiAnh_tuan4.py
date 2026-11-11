"""Bug bash Tuần 4 của B. KHÔNG nộp. Đặt cùng thư mục với solution.py.
Chạy: python -m unittest test_HaiAnh_tuan4 -v
Không thêm tính năng: chỉ kiểm tra ô chết, h_admissible, h_fast, khối 2x2.
"""
import unittest
import solution
from custom_maps import make
from sokoban import PROBLEMS, sokoban_goal_state
from validation import signature, validate_solution

INF = solution.INF


class TestBienOChetVaHeuristic(unittest.TestCase):

    def test_ban_1x1_da_la_dich(self):
        s = make(1, 1, [(0, 0)], [], [(0, 0)])
        self.assertIs(solution.solve(s, 5), s)

    def test_khong_co_thung(self):
        s = make(3, 3, [(0, 0)], [], [(1, 1)])
        self.assertIs(solution.solve(s, 5), s)
        h_adm, h_fast = solution.make_heuristics(s)
        self.assertEqual(h_adm(s), 0)

    def test_thung_da_tren_dich_h_bang_0(self):
        s = make(4, 3, [(0, 1)], [(2, 1)], [(2, 1)])
        h_adm, _ = solution.make_heuristics(s)
        self.assertEqual(h_adm(s), 0)

    def test_nhieu_thung_hon_dich_la_vo_nghiem(self):
        s = make(5, 3, [(0, 0)], [(1, 1), (2, 1)], [(4, 1)])
        h_adm, h_fast = solution.make_heuristics(s)
        self.assertGreaterEqual(h_adm(s), INF)
        self.assertGreaterEqual(h_fast(s), INF)
        self.assertIs(solution.solve(s, 5), False)

    def test_thung_o_goc_chet_ngay_tu_dau(self):
        s = make(5, 3, [(0, 1)], [(0, 0)], [(4, 1)])
        h_adm, h_fast = solution.make_heuristics(s)
        self.assertGreaterEqual(h_adm(s), INF)
        self.assertGreaterEqual(h_fast(s), INF)
        self.assertIs(solution.solve(s, 5), False)

    def test_dich_nhieu_hon_thung(self):
        s = make(5, 3, [(0, 0)], [(1, 0), (2, 1)], [(2, 0), (3, 0), (4, 1)])
        final = solution.solve(s, 10)
        self.assertTrue(validate_solution(s, final)[0])

    def test_nhieu_robot_h_khong_phu_thuoc_so_robot(self):
        a = make(5, 4, [(0, 0)], [(2, 1), (2, 2)], [(4, 1), (4, 2)])
        b = make(5, 4, [(0, 0), (4, 0), (0, 3)], [(2, 1), (2, 2)], [(4, 1), (4, 2)])
        ha, _ = solution.make_heuristics(a)
        hb, _ = solution.make_heuristics(b)
        self.assertEqual(ha(a), hb(b))

    def test_heuristic_khong_sua_state(self):
        for i in (0, 5, 9):
            s = PROBLEMS[i]
            truoc = (signature(s), s.action, s.gval, s.parent, s.robots, s.boxes)
            h_adm, h_fast = solution.make_heuristics(s)
            h_adm(s), h_fast(s)
            for c in s.successors():
                h_adm(c), h_fast(c)
            sau = (signature(s), s.action, s.gval, s.parent, s.robots, s.boxes)
            self.assertEqual(truoc, sau)

    def test_khong_dung_bien_toan_cuc_giua_hai_map(self):
        """Tạo heuristic map A, rồi map B, rồi gọi lại map A: kết quả phải như cũ."""
        a, b = PROBLEMS[1], PROBLEMS[5]
        h_a, _ = solution.make_heuristics(a)
        v1 = h_a(a)
        solution.make_heuristics(b)
        self.assertEqual(h_a(a), v1)
        self.assertEqual(solution.make_heuristics(a)[0](a), v1)

    def test_h_fast_khong_am_va_h_adm_khong_vuot_buoc_that(self):
        opt = [16, 4, 21, 10, 8, 30, 16, 41, 14]
        for i in range(9):
            with self.subTest(map=i):
                s = PROBLEMS[i]
                h_adm, h_fast = solution.make_heuristics(s)
                self.assertLessEqual(h_adm(s), opt[i])
                self.assertGreaterEqual(h_fast(s), h_adm(s))

    def test_thung_tren_o_chet_khong_phai_dich(self):
        s = PROBLEMS[4]
        _, _, dead = solution.tinh_bang(s)
        self.assertTrue(dead.isdisjoint(s.storage))

    def test_goal_ban_dau_khong_bi_cat_boi_2x2(self):
        khoi = [(2, 1), (3, 1), (2, 2), (3, 2)]
        s = make(6, 5, [(0, 0)], khoi, khoi)
        self.assertIs(solution.solve(s, 5), s)


class TestSolveBienThoiGian(unittest.TestCase):

    def test_timebound_0_va_am(self):
        self.assertIs(solution.solve(PROBLEMS[1], 0), False)
        self.assertIs(solution.solve(PROBLEMS[1], -1), False)

    def test_timebound_nho_khong_crash(self):
        for tb in (0.001, 0.05, 0.3):
            r = solution.solve(PROBLEMS[17], tb)
            if r is not False:
                self.assertTrue(validate_solution(PROBLEMS[17], r)[0])

    def test_initial_state_khong_bi_doi(self):
        s = PROBLEMS[9]
        truoc = (signature(s), s.action, s.gval, s.parent)
        solution.solve(s, 3)
        self.assertEqual(truoc, (signature(s), s.action, s.gval, s.parent))


if __name__ == "__main__":
    unittest.main()
