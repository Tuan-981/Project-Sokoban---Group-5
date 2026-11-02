""" 5 map tự tạo để kiểm thử biên. KHÔNG nộp file này, Solution không được IMPORT nó.
Mỗi phần tử: (tên, trạng thái ban đầu, số bước tối ưu mông đợi)
None có nghĩa là vô nghiệm, solve nghĩa là trả về false."""

from sokoban import SokobanState

def make(width, height, robots, boxes, storage, obstacles=()) :
    """Tạo trạng thái thừ đầu dữ liệu thô."""
    return SokobanState("START", 0, None, width, height, tuple(robots),
                        frozenset(boxes), frozenset(storage), frozenset(obstacles))

MAPS = [
    ("vo_nghiem_goc",
    make(4, 3, [(0, 2)], [(3, 0)], [(1, 1)]), None),
    ("dich_nhieu_hon_thung",
    make(5, 3, [(0, 0)], [(1, 0), (2, 1)], [(2, 0), (3, 0), (4, 1)]), 4),
    ("thung_da_o_dich",
     make(5, 3, [(0, 1)], [(1, 1), (3, 1)], [(1, 1), (4, 1)]), 5),
    ("mot_robot_re_goc",
     make(5, 4, [(0, 0)], [(2, 1)], [(4, 3)]), 8),
    ("nhieu_robot",
     make(5, 4, [(0, 0), (4, 0), (0, 3)], [(2, 1), (2, 2)], [(4, 1), (4, 2)]), 8), 
]
