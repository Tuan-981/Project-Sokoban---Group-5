"""Student entry point. See README.md for the API and scoring rules.

Tuần 2: Bản tích hợp hoàn chỉnh đỉnh cao:
  - Thuật toán tìm kiếm A* (Người A - Hồ Anh Tuấn phụ trách Vùng 4, 5).
  - Ô chết (Dead squares) & Heuristic h2 Ghép cặp Bitmask DP tối ưu (Người B - Nghiêm Nguyễn Hải Anh phụ trách Vùng 2, 3).
"""
import heapq
import itertools
from collections import deque
from time import perf_counter
from sokoban import sokoban_goal_state


# ===== VÙNG 1: Tiện ích chung và thống kê (C) =====
LAST_STATS = {
    "expanded": 0,   # Số node được lấy khỏi frontier để mở rộng
    "generated": 0,  # Tổng số trạng thái con được sinh ra
    "unique": 0,     # Số trạng thái duy nhất được phát hiện
    "elapsed": 0.0,  # Thời gian chạy tính bằng giây
    "status": "NOT_RUN",  # NOT_RUN, RUNNING, SOLVED, TIMEOUT hoặc FAILED
}


# ===== VÙNG 2: Ô chết và bảng khoảng cách (B - Hải Anh) =====

def trong_ban_va_trong(state, c):
    """
    Kiểm tra ô c có nằm trong bàn cờ và không phải tường hay không.
    """
    x, y = c
    if not (0 <= x < state.width and 0 <= y < state.height):
        return False
    if c in state.obstacles:
        return False
    return True


def bfs_nguoc(state, g):
    """
    BFS ngược từ một ô đích g để tính khoảng cách đẩy từ các ô khác đến g.
    dist[c] là số lần đẩy ít nhất để đưa một thùng từ ô c đến đích g.
    """
    dist = {g: 0}
    queue = deque([g])
    directions = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0)
    ]

    while queue:
        c = queue.popleft()
        x, y = c

        for dx, dy in directions:
            # p: vị trí trước đó của thùng
            # r: vị trí robot cần đứng để đẩy thùng từ p đến c
            p = (x - dx, y - dy)
            r = (x - 2 * dx, y - 2 * dy)

            if not trong_ban_va_trong(state, p):
                continue
            if not trong_ban_va_trong(state, r):
                continue
            if p in dist:
                continue

            dist[p] = dist[c] + 1
            queue.append(p)

    return dist


def tinh_bang(initial_state):
    """
    Tạo ba cấu trúc dữ liệu:
      - dist: Bảng khoảng cách riêng từ từng ô đến từng đích.
      - dist_to_goal: Khoảng cách đẩy nhỏ nhất từ mỗi ô đến một đích bất kỳ.
      - dead: Tập các ô chết (không thể đẩy thùng từ đó đến bất kỳ đích nào).
    """
    dist = {}
    for goal in initial_state.storage:
        dist[goal] = bfs_nguoc(initial_state, goal)

    dist_to_goal = {}
    for goal_distances in dist.values():
        for cell, distance in goal_distances.items():
            if cell not in dist_to_goal or distance < dist_to_goal[cell]:
                dist_to_goal[cell] = distance

    dead = set()
    for x in range(initial_state.width):
        for y in range(initial_state.height):
            cell = (x, y)
            if cell in initial_state.obstacles:
                continue
            if cell not in dist_to_goal:
                dead.add(cell)

    return dist, dist_to_goal, dead


# ===== VÙNG 3: Các hàm Heuristic (B - Hải Anh) =====

INF = 10**9


def make_heuristic(initial_state):
    """
    Heuristic h1: Tổng khoảng cách đẩy ngắn nhất từ mỗi thùng đến đích gần nhất.
    """
    dist, dist_to_goal, dead = tinh_bang(initial_state)
    cache = {}

    def h(s):
        boxes = s.boxes
        key = tuple(sorted(boxes))

        if key in cache:
            return cache[key]

        total = 0
        for box in boxes:
            if box not in dist_to_goal:
                total = INF
                break
            total += dist_to_goal[box]

        cache[key] = total
        return total

    return h


def make_heuristic_h2(initial_state):
    """
    Heuristic h2: Ghép cặp thùng–đích tối ưu (1-1) bằng Quy hoạch động Bitmask.
    Mỗi thùng chỉ được vào một ô đích riêng biệt.
    h2(s) >= h1(s) và hoàn toàn admissible.
    """
    dist, dist_to_goal, dead = tinh_bang(initial_state)
    goals = list(initial_state.storage)
    ng = len(goals)

    if ng > 16:
        # Nếu số đích quá lớn, tự động fallback về h1 để tránh bùng nổ bitmask
        return make_heuristic(initial_state)

    full = 1 << ng
    popcount = [bin(m).count("1") for m in range(full)]
    cache = {}

    def h(s):
        boxes = s.boxes
        key = tuple(sorted(boxes))

        if key in cache:
            return cache[key]

        box_list = list(boxes)
        n = len(box_list)

        # Nếu số thùng nhiều hơn số đích -> Vô nghiệm
        if n > ng:
            cache[key] = INF
            return INF

        # Kiểm tra nhanh: nếu có thùng rơi vào ô chết -> cắt tỉa ngay
        for b in box_list:
            if b not in dist_to_goal:
                cache[key] = INF
                return INF

        # Ma trận chi phí: cost[i][j] là khoảng cách đẩy từ thùng i tới đích j
        cost = [[dist[g].get(b, INF) for g in goals] for b in box_list]

        # dp[mask] = tổng khoảng cách nhỏ nhất khi các đích trong mask đã được ghép
        dp = [INF] * full
        dp[0] = 0

        for mask in range(full):
            cur = dp[mask]
            if cur >= INF:
                continue

            i = popcount[mask]
            if i >= n:
                continue

            for j in range(ng):
                if (mask >> j) & 1:
                    continue

                c = cost[i][j]
                if c >= INF:
                    continue

                nm = mask | (1 << j)
                v = cur + c
                if v < dp[nm]:
                    dp[nm] = v

        best = min((dp[m] for m in range(full) if popcount[m] == n), default=INF)
        result = best if best < INF else INF

        cache[key] = result
        return result

    return h


# ===== VÙNG 4: Thuật toán tìm kiếm A* (A - Tuấn) =====

def a_star_search(initial_state, heuristic_fn, timebound, started):
    """
    Thuật toán tìm kiếm A* chuẩn:
      f(s) = g(s) + h(s)
    """
    global LAST_STATS
    deadline = started + timebound
    tie_counter = itertools.count()

    h_init = heuristic_fn(initial_state)
    if h_init >= INF:
        LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
        return False

    frontier = []
    f_init = initial_state.gval + h_init
    heapq.heappush(frontier, (f_init, next(tie_counter), initial_state))

    init_key = initial_state.hashable_state()
    best_g = {init_key: initial_state.gval}
    LAST_STATS["unique"] = 1

    while frontier:
        if perf_counter() >= deadline:
            LAST_STATS.update(elapsed=perf_counter() - started, status="TIMEOUT")
            return False

        f_val, _, current = heapq.heappop(frontier)
        curr_key = current.hashable_state()

        if current.gval > best_g.get(curr_key, current.gval):
            continue

        LAST_STATS["expanded"] += 1

        # Goal test khi POP
        if sokoban_goal_state(current):
            LAST_STATS.update(elapsed=perf_counter() - started, status="SOLVED")
            return current

        successors = current.successors()
        LAST_STATS["generated"] += len(successors)

        for child in successors:
            child_key = child.hashable_state()

            if child_key in best_g and child.gval >= best_g[child_key]:
                continue

            h_val = heuristic_fn(child)

            # Cắt tỉa trạng thái rơi vào ô chết hoặc không có cách ghép hợp lệ
            if h_val >= INF:
                continue

            if child_key not in best_g:
                LAST_STATS["unique"] += 1
            best_g[child_key] = child.gval

            f_child = child.gval + h_val
            heapq.heappush(frontier, (f_child, next(tie_counter), child))

    LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
    return False


# ===== VÙNG 5: Hàm solve() và quản lý thời gian (A - Tuấn) =====

def solve(initial_state, timebound=120):
    """
    Entry point giải Sokoban bằng A* kết hợp Heuristic h2 Ghép cặp Bitmask DP.
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

    if timebound <= 0:
        LAST_STATS.update(elapsed=perf_counter() - started, status="TIMEOUT")
        return False

    if sokoban_goal_state(initial_state):
        LAST_STATS.update(
            unique=1,
            elapsed=perf_counter() - started,
            status="SOLVED",
        )
        return initial_state

    # KÍCH HOẠT HEURISTIC h2 (Ghép cặp 1-1 tối ưu)
    heuristic_fn = make_heuristic_h2(initial_state)

    return a_star_search(initial_state, heuristic_fn, timebound, started)
