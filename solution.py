"""Student entry point. See README.md for the API and scoring rules.

Tuần 2: Nâng cấp baseline sang thuật toán A* (Người A - Tuấn phụ trách Vùng 4, 5).
Hỗ trợ tích hợp Heuristic h1 / h2 và cắt tỉa ô chết (Người B - Hải Anh phụ trách Vùng 2, 3).
"""
import heapq
import itertools
from time import perf_counter
from sokoban import sokoban_goal_state


# ===== VÙNG 1: Tiện ích chung và thống kê (C) =====
# Thống kê lần chạy gần nhất; không làm thay đổi API của solve().
LAST_STATS = {
    "expanded": 0,   # Số node được lấy khỏi frontier để mở rộng
    "generated": 0,  # Tổng số trạng thái con được sinh ra
    "unique": 0,     # Số trạng thái duy nhất được phát hiện
    "elapsed": 0.0,  # Thời gian chạy tính bằng giây
    "status": "NOT_RUN",  # NOT_RUN, RUNNING, SOLVED, TIMEOUT hoặc FAILED
}


# ===== VÙNG 2: Ô chết và bảng khoảng cách (B) =====
# (Người B - Hải Anh sẽ viết các hàm tính dead squares và BFS ngược khoảng cách tại đây)


# ===== VÙNG 3: Các hàm Heuristic (B) =====
# Hằng số đại diện cho vô cùng lớn (trạng thái vô nghiệm / rơi vào ô chết)
INF = 10**9

def default_heuristic(state):
    """
    Heuristic mặc định h = 0 khi chưa ghép hàm của B.
    Với h = 0, A* hoạt động tương đương thuật toán Dijkstra/BFS tối ưu số bước.
    """
    return 0


# ===== VÙNG 4: Thuật toán tìm kiếm A* / Weighted A* (A) =====

def a_star_search(initial_state, heuristic_fn, timebound, started):
    """
    Thuật toán tìm kiếm A* chuẩn (Graph-Search A*):
      f(s) = g(s) + h(s)
    
    Quy chuẩn cài đặt theo cam kết nhóm:
      1. Hàng đợi ưu tiên heapq (min-heap) lưu tuple: (f, tie_counter, state)
      2. Bộ đếm tie_counter tránh lỗi so sánh trực tiếp 2 SokobanState khi cùng f.
      3. Quản lý chi phí tốt nhất bằng từ điển best_g: {hashable_state: best_gval}.
      4. Goal test khi POP (lấy node ra khỏi heap) để đảm bảo tính tối ưu.
      5. Cắt tỉa ngay trạng thái có h >= INF (rơi vào ô chết).
      6. Đo lường chính xác các chỉ số thống kê expanded, generated, unique.
    """
    global LAST_STATS
    deadline = started + timebound
    tie_counter = itertools.count()

    # Tính heuristic cho trạng thái khởi đầu
    h_init = heuristic_fn(initial_state)
    if h_init >= INF:
        # Trạng thái đầu đã vô nghiệm (thùng kẹt ô chết từ đầu)
        LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
        return False

    # Hàng đợi ưu tiên frontier (min-heap)
    # Lưu: (f_score, tie_breaker, state)
    frontier = []
    f_init = initial_state.gval + h_init
    heapq.heappush(frontier, (f_init, next(tie_counter), initial_state))

    # Từ điển theo dõi chi phí gval nhỏ nhất từng tìm thấy tới cấu hình (robots, boxes)
    init_key = initial_state.hashable_state()
    best_g = {init_key: initial_state.gval}
    LAST_STATS["unique"] = 1

    while frontier:
        # Kiểm tra giới hạn thời gian ở đầu mỗi vòng lặp
        if perf_counter() >= deadline:
            LAST_STATS.update(elapsed=perf_counter() - started, status="TIMEOUT")
            return False

        # Lấy trạng thái có f(s) nhỏ nhất ra khỏi frontier
        f_val, _, current = heapq.heappop(frontier)
        curr_key = current.hashable_state()

        # Nếu đã tìm thấy một đường đi khác đến trạng thái này với chi phí gval nhỏ hơn, bỏ qua node cũ
        if current.gval > best_g.get(curr_key, current.gval):
            continue

        # Đếm node mở rộng thực tế (expanded)
        LAST_STATS["expanded"] += 1

        # KIỂM TRA ĐÍCH KHI POP (Goal test on POP) - Đảm bảo lời giải tìm thấy đầu tiên là tối ưu
        if sokoban_goal_state(current):
            LAST_STATS.update(elapsed=perf_counter() - started, status="SOLVED")
            return current

        # Sinh các trạng thái con hợp lệ
        successors = current.successors()
        LAST_STATS["generated"] += len(successors)

        for child in successors:
            child_key = child.hashable_state()

            # Nếu đường đi mới không tốt hơn đường đã biết, không duyệt
            if child_key in best_g and child.gval >= best_g[child_key]:
                continue

            # Tính heuristic cho trạng thái con
            h_val = heuristic_fn(child)

            # CẮT TỈA Ô CHẾT: Thùng rơi vào ô chết hoặc nhánh bế tắc -> bỏ qua ngay
            if h_val >= INF:
                continue

            # Ghi nhận trạng thái mới hoặc đường đi ngắn hơn tới trạng thái cũ
            if child_key not in best_g:
                LAST_STATS["unique"] += 1
            best_g[child_key] = child.gval

            # Tính f(child) = g(child) + h(child) và đưa vào frontier
            f_child = child.gval + h_val
            heapq.heappush(frontier, (f_child, next(tie_counter), child))

    # Duyệt hết không gian trạng thái mà không có đường tới đích -> Vô nghiệm
    LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
    return False


# ===== VÙNG 5: Hàm solve() và quản lý thời gian (A) =====

def solve(initial_state, timebound=120):
    """
    Entry point giải Sokoban bằng thuật toán A*.

    Args:
        initial_state: Trạng thái xuất phát (SokobanState) - chỉ đọc.
        timebound: Giới hạn thời gian (giây).

    Returns:
        SokobanState: Trạng thái đích với chuỗi parent hợp lệ.
        False: Nếu timeout hoặc vô nghiệm.
    """
    global LAST_STATS
    started = perf_counter()
    LAST_STATS = {
        "expanded": 0,
        "generated": 0,
        "unique": 0,
        "elapsed": 0.0,
        "status": "RUNNING",
    }

    # Hết thời gian ngay từ đầu hoặc timebound không hợp lệ -> trả về False
    if timebound <= 0:
        LAST_STATS.update(elapsed=perf_counter() - started, status="TIMEOUT")
        return False

    # Trường hợp đặc biệt: Trạng thái đầu đã là đích
    if sokoban_goal_state(initial_state):
        LAST_STATS.update(
            unique=1,
            elapsed=perf_counter() - started,
            status="SOLVED",
        )
        return initial_state

    # Khởi tạo hàm heuristic:
    # Ở giai đoạn hiện tại (trước khi B ghép h1), dùng default_heuristic (h = 0)
    # Sau này Thứ 5 chỉ cần đổi dòng này thành: heuristic_fn = make_heuristic(initial_state)
    heuristic_fn = default_heuristic

    # Gọi thuật toán A* tìm kiếm
    return a_star_search(initial_state, heuristic_fn, timebound, started)
