"""Student entry point. See README.md for the API and scoring rules.

Tuần 1: Baseline BFS chuẩn của nhóm (Nền tảng logic của bạn Trâm kết hợp tối ưu thời gian perf_counter của bạn Long).
"""
from collections import deque
from time import perf_counter
from sokoban import sokoban_goal_state


# ===== VÙNG 1: Tiện ích chung và thống kê (C) =====
# (Dành cho việc đo đạc, thống kê node mở rộng / thời gian ở các tuần tiếp theo)
# Thống kê lần chạy gần nhất; không làm thay đổi API của solve().
LAST_STATS = {
    "expanded": 0,   # Số node được lấy khỏi frontier để mở rộng
    "generated": 0,  # Tổng số trạng thái con được sinh ra
    "unique": 0,     # Số trạng thái duy nhất được phát hiện
    "elapsed": 0.0,  # Thời gian chạy tính bằng giây
    "status": "NOT_RUN",  # NOT_RUN, RUNNING, SOLVED, TIMEOUT hoặc FAILED
}


# ===== VÙNG 2: Ô chết và bảng khoảng cách (B) =====
# (Dành cho Tuần 2)


# ===== VÙNG 3: Các hàm Heuristic (B) =====
# (Dành cho Tuần 2)


# ===== VÙNG 4: Thuật toán tìm kiếm A* / Weighted A* (A) =====
# (Dành cho Tuần 2 và Tuần 3)


# ===== VÙNG 5: Hàm solve() và quản lý thời gian (A) =====

def solve(initial_state, timebound=120):
    """
    Tìm kiếm lời giải Sokoban bằng giải thuật BFS (Breadth-First Search).
    Đảm bảo tìm ra đường đi ngắn nhất (tối ưu số bước) vì mọi hành động có chi phí bằng 1.

    Args:
        initial_state: Trạng thái xuất phát (SokobanState) - chỉ đọc, không sửa.
        timebound: Ngân sách thời gian tối đa cho phép (giây).

    Returns:
        SokobanState: Trạng thái đích với chuỗi parent hợp lệ để dựng đường đi.
        False: Nếu hết thời gian hoặc không tìm thấy đường đi (vô nghiệm).
    """
    # Khởi tạo thống kê cho lần chạy hiện tại; giữ nguyên giá trị trả về của solve().
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

    # Sử dụng perf_counter (từ code bạn Long) để đo thời gian đơn điệu, không bị lệch giờ hệ thống
    deadline = started + timebound

    # Trạng thái đầu đã là đích thì trả về chính nó (gval = 0, parent = None)
    if sokoban_goal_state(initial_state):
        LAST_STATS.update(
            unique=1,
            elapsed=perf_counter() - started,
            status="SOLVED",
        )
        return initial_state

    # Khởi tạo hàng đợi biên (frontier) và tập trạng thái đã duyệt (visited)
    frontier = deque([initial_state])
    visited = {initial_state.hashable_state()}
    LAST_STATS["unique"] = 1

    while frontier:
        # Kiểm tra giới hạn thời gian ở đầu vòng lặp (theo cách bạn Trâm, tránh overhead trong vòng for)
        if perf_counter() >= deadline:
            return False

        # Lấy trạng thái ở đầu hàng đợi ra để mở rộng (cơ chế FIFO)
        current = frontier.popleft()
        LAST_STATS["expanded"] += 1

        # Duyệt các trạng thái con hợp lệ
        successors = current.successors()
        LAST_STATS["generated"] += len(successors)
        for child in successors:
            key = child.hashable_state()

            # Bỏ qua nếu cấu hình này đã từng được ghé thăm
            if key in visited:
                continue

            # Kiểm tra đích ngay khi sinh trạng thái con (Goal test on generation)
            # Với BFS chi phí đơn vị, đích tìm thấy đầu tiên luôn đảm bảo số bước tối ưu
            if sokoban_goal_state(child):
                LAST_STATS["unique"] += 1
                LAST_STATS.update(
                    elapsed=perf_counter() - started,
                    status="SOLVED",
                )
                return child

            # Đánh dấu đã thăm và đưa vào cuối hàng đợi frontier
            visited.add(key)
            LAST_STATS["unique"] += 1
            frontier.append(child)

    # Hết hàng đợi mà không tìm thấy đích (map vô nghiệm) -> trả về False
    LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
    return False
