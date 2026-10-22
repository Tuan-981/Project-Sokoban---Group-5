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
from collections import deque

def trong_ban_va_trong(state, c):
    """
    Kiểm tra ô c có nằm trong bàn cờ và không phải tường hay không.

    state: trạng thái Sokoban ban đầu.
    c: tọa độ ô, có dạng (x, y).

    Trả về:
        True nếu ô nằm trong bàn và không phải tường.
        False nếu ô nằm ngoài bàn hoặc là tường.
    """
    x, y = c

    # Kiểm tra tọa độ nằm trong giới hạn bàn cờ
    if not (0 <= x < state.width and 0 <= y < state.height):
        return False

    # Kiểm tra ô có phải tường hay không
    if c in state.obstacles:
        return False

    return True


def bfs_nguoc(state, g):
    """
    BFS ngược từ một ô đích g để tính khoảng cách đẩy
    từ các ô khác đến g.

    dist[c] là số lần đẩy ít nhất để đưa một thùng
    từ ô c đến đích g, xét các điều kiện đẩy hợp lệ.

    Lưu ý:
        Không sử dụng vị trí robot hoặc vị trí thùng hiện tại
        làm tường.
    """
    # Khoảng cách từ đích đến chính nó bằng 0
    dist = {g: 0}

    # Hàng đợi BFS
    queue = deque([g])

    # Bốn hướng di chuyển: lên, xuống, trái, phải
    directions = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0)
    ]

    while queue:
        # Ô hiện tại đang xét
        c = queue.popleft()
        x, y = c

        for dx, dy in directions:
            # p: vị trí trước đó của thùng
            # r: vị trí robot cần đứng để đẩy thùng từ p đến c
            p = (x - dx, y - dy)
            r = (x - 2 * dx, y - 2 * dy)

            # Cả vị trí thùng trước đó và vị trí robot
            # đều phải nằm trong bàn và không phải tường
            if not trong_ban_va_trong(state, p):
                continue

            if not trong_ban_va_trong(state, r):
                continue

            # Nếu đã thăm ô p thì không thêm lại
            if p in dist:
                continue

            # Khoảng cách đến đích tăng thêm một lần đẩy
            dist[p] = dist[c] + 1

            # Đưa ô mới vào hàng đợi
            queue.append(p)

    return dist


def tinh_bang(initial_state):
    """
    Tạo ba cấu trúc dữ liệu:

    dist:
        Bảng khoảng cách riêng từ từng ô đến từng đích.
        Dùng cho heuristic nâng cao sau này.

    dist_to_goal:
        Khoảng cách đẩy nhỏ nhất từ mỗi ô đến một đích bất kỳ.

    dead:
        Tập các ô không phải tường nhưng không thể đẩy thùng
        từ đó đến bất kỳ đích nào.
    """

    # Bảng khoảng cách riêng cho từng đích
    dist = {}

    for goal in initial_state.storage:
        dist[goal] = bfs_nguoc(initial_state, goal)

    # Khoảng cách ngắn nhất từ mỗi ô đến một đích bất kỳ
    dist_to_goal = {}

    for goal_distances in dist.values():
        for cell, distance in goal_distances.items():

            # Chưa có khoảng cách thì thêm vào
            if cell not in dist_to_goal:
                dist_to_goal[cell] = distance

            # Nếu đã có, giữ khoảng cách nhỏ hơn
            elif distance < dist_to_goal[cell]:
                dist_to_goal[cell] = distance

    # Tìm các ô chết
    dead = set()

    for x in range(initial_state.width):
        for y in range(initial_state.height):
            cell = (x, y)

            # Tường không được xem là ô chết
            if cell in initial_state.obstacles:
                continue

            # Ô trống không thể đi đến bất kỳ đích nào
            # được xem là dead square
            if cell not in dist_to_goal:
                dead.add(cell)

    return dist, dist_to_goal, dead


# ===== VÙNG 3: Các hàm Heuristic (B) =====
# (Dành cho Tuần 2)

# Giá trị rất lớn, dùng để biểu thị trạng thái không thể giải
INF = 10**9


def make_heuristic(initial_state):
    """
    Tạo heuristic h1 cho thuật toán tìm kiếm Sokoban.

    h1(s) = tổng khoảng cách đẩy ngắn nhất từ mỗi thùng
            đến một đích gần nhất.

    Nếu có thùng nằm ở ô chết, trả về INF.

    Không sửa đổi trạng thái s.
    """

    # Tạo bảng khoảng cách và tập ô chết từ trạng thái ban đầu
    dist, dist_to_goal, dead = tinh_bang(initial_state)

    # Bộ nhớ đệm kết quả heuristic
    cache = {}

    def h(s):
        # Chỉ sử dụng vị trí các thùng, không xét vị trí robot
        boxes = s.boxes

        # Chuẩn hóa thành tuple để dùng làm khóa,
        # kể cả khi s.boxes là set
        key = tuple(sorted(boxes))

        # Nếu đã tính trước đó thì dùng lại kết quả
        if key in cache:
            return cache[key]

        total = 0

        for box in boxes:
            # Thùng không thể đến bất kỳ đích nào
            if box not in dist_to_goal:
                total = INF
                break

            # Cộng khoảng cách đẩy ngắn nhất đến một đích
            total += dist_to_goal[box]

        # Lưu kết quả để tránh tính lại
        cache[key] = total

        return total

    return h


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
    # Kiểm tra giới hạn thời gian ở đầu vòng lặp
        if perf_counter() >= deadline:
            LAST_STATS.update(
                elapsed=perf_counter() - started,
                status="TIMEOUT",  #Khi hết thời gian, hàm trả về False ngay lập tức cập nhật LAST_STATS["status"] từ "RUNNING" thành "TIMEOUT".
            )
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
