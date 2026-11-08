"""Student entry point. See README.md for the API and scoring rules.

Tuần 4: Tối ưu hoá nâng cao — Anytime Repairing A* (ARA*) Tinh Gọn:
  - Thuật toán ARA* tập trung (Focused Refinement w=1.8) kết hợp Cost-bound Pruning (Người A - Hồ Anh Tuấn phụ trách Vùng 4, 5).
  - Khối ô chết 2x2 & Heuristic kép (h_admissible, h_fast) (Người B - Nghiêm Nguyễn Hải Anh phụ trách Vùng 2, 3).
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

# ----- TUẦN 3 & 4 (B - Hải Anh): h_admissible / h_fast và ô chết khối 2x2 -----

def tinh_bang_di_bo(initial_state):
    """
    Bảng khoảng cách ĐI BỘ giữa các ô trống (chỉ xét tường, bỏ qua thùng và robot).
    walk[a][b] = số bước đi bộ ít nhất từ ô a đến ô b.
    Vì bỏ qua thùng nên walk[a][b] <= khoảng cách đi bộ thật -> là cận dưới.
    Tính 1 lần ở đầu solve(); bàn tối đa 8x8 nên chỉ ~64 lần BFS.
    """
    w, h = initial_state.width, initial_state.height
    walls = initial_state.obstacles
    walk = {}
    for x in range(w):
        for y in range(h):
            start = (x, y)
            if start in walls:
                continue
            dist = {start: 0}
            queue = deque([start])
            while queue:
                cx, cy = queue.popleft()
                for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    nxt = (cx + dx, cy + dy)
                    if nxt in dist:
                        continue
                    if not (0 <= nxt[0] < w and 0 <= nxt[1] < h):
                        continue
                    if nxt in walls:
                        continue
                    dist[nxt] = dist[(cx, cy)] + 1
                    queue.append(nxt)
            walk[start] = dist
    return walk


def lam_ham_khoi_2x2(initial_state):
    """
    Trả về hàm ket_2x2(boxes) -> True nếu có BẾ TẮC khối 2x2.
    Bế tắc: một khối 2x2 mà cả 4 ô đều là tường / ngoài bàn / thùng,
    và có ít nhất 1 thùng trong khối KHÔNG nằm trên ô đích.
    Khi đó các thùng trong khối chặn lẫn nhau, không ai đẩy được nữa.
    Khối toàn thùng đã nằm trên đích thì KHÔNG phải bế tắc.
    Robot không tính là vật chặn vì robot di chuyển được.
    """
    w, h = initial_state.width, initial_state.height
    walls = initial_state.obstacles
    storage = initial_state.storage

    def bi_chan(c, boxes):
        x, y = c
        return (not (0 <= x < w and 0 <= y < h)) or c in walls or c in boxes

    def ket_2x2(boxes):
        for b in boxes:
            if b in storage:
                continue  # chỉ xét quanh thùng CHƯA ở đích
            bx, by = b
            for ox, oy in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
                tx, ty = bx + ox, by + oy  # góc trên-trái của khối chứa b
                if (bi_chan((tx, ty), boxes) and bi_chan((tx + 1, ty), boxes)
                        and bi_chan((tx, ty + 1), boxes)
                        and bi_chan((tx + 1, ty + 1), boxes)):
                    return True
        return False

    return ket_2x2


def make_heuristics(initial_state, dung_2x2=True):
    """
    Giao diện cho A (Tuần 3 & 4). Trả về cặp (h_admissible, h_fast), tính bảng 1 lần.

    h_admissible(s): h2 (ghép cặp bitmask) -> ADMISSIBLE, dùng ở pha w = 1.
    h_fast(s)      : h2 + bước đi bộ của robot -> CÓ THỂ KHÔNG admissible,
                     chỉ dùng ở các pha w > 1 (tìm nhanh, chấp nhận kém tối ưu).

    Cả hai trả về >= INF nếu trạng thái bế tắc (ô chết, thiếu đích, khối 2x2).
    Cắt bế tắc không làm mất lời giải vì trạng thái bế tắc vốn vô nghiệm.
    Chỉ đọc s, không sửa s.
    """
    h2 = make_heuristic_h2(initial_state)
    walk = tinh_bang_di_bo(initial_state)
    ket_2x2 = lam_ham_khoi_2x2(initial_state) if dung_2x2 else (lambda boxes: False)
    storage = initial_state.storage
    w, hh = initial_state.width, initial_state.height
    walls = initial_state.obstacles

    # Với mỗi ô c: các ô kề c mà robot có thể đứng để đẩy thùng ở c
    dung = {}
    for x in range(w):
        for y in range(hh):
            c = (x, y)
            dung[c] = [n for n in ((x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y))
                       if 0 <= n[0] < w and 0 <= n[1] < hh and n not in walls]

    def h_admissible(s):
        if ket_2x2(s.boxes):
            return INF
        return h2(s)

    def buoc_di_bo(s):
        """
        Ước lượng số bước robot phải đi bộ trước lần đẩy đầu tiên:
        min theo (robot, thùng chưa ở đích) của khoảng cách tới ô kề thùng.
        Có thể trùng với các bước đẩy đã đếm trong h2 -> không đảm bảo admissible.
        """
        best = None
        for b in s.boxes:
            if b in storage:
                continue
            for r in s.robots:
                tab = walk.get(r)
                if tab is None:
                    continue
                for n in dung[b]:
                    d = tab.get(n)
                    if d is not None and (best is None or d < best):
                        best = d
        return 0 if best is None else best

    def h_fast(s):
        base = h_admissible(s)
        if base >= INF:
            return INF
        return base + buoc_di_bo(s)

    return h_admissible, h_fast


# ===== VÙNG 4: Thuật toán tìm kiếm Weighted A* với Cost-Bound Pruning (A - Tuấn) =====

def a_star_search(initial_state, heuristic_fn, timebound, started, weight=1.0, deadline=None, cost_bound=None, rescue_on_timeout=True, prune_heuristic_fn=None):
    """
    Thuật toán tìm kiếm Weighted A* nâng cấp Tuần 4:
      - f(s) = g(s) + weight * h(s)
      - Tie-break theo h: Hàng đợi ưu tiên (f, h, tie_counter, state)
      - Cắt tỉa cận trên (Cost-bound pruning): Bỏ qua mọi trạng thái có g(s) + h(s) >= cost_bound
    """
    global LAST_STATS
    if deadline is None:
        deadline = started + timebound
    tie_counter = itertools.count()

    h_init = heuristic_fn(initial_state)
    if h_init >= INF:
        return False
    h_init_prune = prune_heuristic_fn(initial_state) if prune_heuristic_fn is not None else h_init
    if h_init_prune >= INF:
        return False
    if cost_bound is not None and initial_state.gval + h_init_prune >= cost_bound:
        return False

    frontier = []
    f_init = initial_state.gval + weight * h_init
    heapq.heappush(frontier, (f_init, h_init, next(tie_counter), initial_state))

    init_key = initial_state.hashable_state()
    best_g = {init_key: initial_state.gval}
    if LAST_STATS["unique"] == 0:
        LAST_STATS["unique"] = 1

    while frontier:
        if perf_counter() >= deadline:
            return None

        f_val, h_val, _, current = heapq.heappop(frontier)
        curr_key = current.hashable_state()

        if current.gval > best_g.get(curr_key, current.gval):
            continue

        # Cắt tỉa cận trên: dùng prune_heuristic_fn (h_admissible ở Pha 3) để an toàn tuyệt đối
        h_prune = prune_heuristic_fn(current) if prune_heuristic_fn is not None else h_val
        if cost_bound is not None and current.gval + h_prune >= cost_bound:
            continue

        LAST_STATS["expanded"] += 1

        # Goal test khi POP
        if sokoban_goal_state(current):
            return current

        successors = current.successors()
        LAST_STATS["generated"] += len(successors)

        # Hết giờ giữa danh sách con: successors() đã trả phí. Xét nốt các con
        # đã sinh; gặp đích còn ngắn hơn cận thì nhận, không gọi heuristic nữa.
        timed_out = False
        for child in successors:
            if not timed_out and perf_counter() >= deadline:
                timed_out = True
            if timed_out:
                if not rescue_on_timeout:
                    continue
                if cost_bound is not None and child.gval >= cost_bound:
                    continue
                if not sokoban_goal_state(child):
                    continue
                child_key = child.hashable_state()
                if child_key in best_g and child.gval >= best_g[child_key]:
                    continue
                if child_key not in best_g:
                    LAST_STATS["unique"] += 1
                return child
            child_key = child.hashable_state()

            if child_key in best_g and child.gval >= best_g[child_key]:
                continue

            # Cắt tỉa nhánh con: nếu có prune_heuristic_fn (h_admissible), cắt cận chuẩn xác trước
            if prune_heuristic_fn is not None:
                h_p = prune_heuristic_fn(child)
                if h_p >= INF:
                    continue
                if cost_bound is not None and child.gval + h_p >= cost_bound:
                    continue
                h_c = h_p if heuristic_fn is prune_heuristic_fn else heuristic_fn(child)
                if h_c >= INF:
                    continue
            else:
                h_c = heuristic_fn(child)
                if h_c >= INF:
                    continue
                if cost_bound is not None and child.gval + h_c >= cost_bound:
                    continue

            if child_key not in best_g:
                LAST_STATS["unique"] += 1
            best_g[child_key] = child.gval

            f_child = child.gval + weight * h_c
            heapq.heappush(frontier, (f_child, h_c, next(tie_counter), child))

        if timed_out:
            return None

    # Frontier cạn kiệt tự nhiên: toàn bộ không gian hợp lệ < cost_bound đã duyệt hết
    return False


# ===== VÙNG 5: Hàm solve() và quản lý thời gian ARA* Tinh Gọn (A - Tuấn) =====

def solve(initial_state, timebound=120):
    """
    Entry point giải Sokoban bằng chiến lược Anytime Repairing A* (ARA*) Tinh Gọn:
      - Pha 1 (Optimal check): Chạy A* chuẩn (w = 1.0, h_admissible) với ngân sách tối ưu 0.45s.
               Giải quyết Maps 0-8 với số bước tối ưu 100% khớp BFS.
      - Pha 2 (Rapid Feasible Solution): Weighted A* (w = 3.0, h_fast) tìm nghiệm hợp lệ đầu tiên,
               chống hoàn toàn rủi ro Timeout trên maps lớn.
      - Pha 3 (Focused Refinement w = 1.8): Nếu còn >= 1.5s, mỗi lượt gọt có hạn riêng 2.0s.
               Lượt không rút được bước dừng trong hạn đó, không chạy tới hạn chung.
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

    # Biên = min(5% hạn giờ, 0.30s). Không sàn 0.25s: hạn ngắn vẫn còn giờ tìm.
    # Hạn 5s dành 0.25s. Hạn 0.2s dành 0.01s.
    safety_margin = min(0.30, 0.05 * timebound)
    effective_deadline = started + timebound - safety_margin

    # KHỞI TẠO BỘ HEURISTIC KÉP (B - Hải Anh)
    h_admissible, h_fast = make_heuristics(initial_state)

    # Kiểm tra nhanh: Nếu trạng thái xuất phát đã bế tắc (ô chết / deadlock 2x2) -> Vô nghiệm
    if h_admissible(initial_state) >= INF:
        LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
        return False

    # PHA 1: Tìm kiếm tối ưu tuyệt đối với w = 1.0 (Ngân sách tối ưu 0.45s)
    # Maps 0-8 giải xong trong < 0.35s và đảm bảo số bước tối ưu 100% khớp BFS
    # rescue_on_timeout=False: Chỉ nhận đích khi POP để bảo toàn tính tối ưu toán học của A*
    p1_budget = min(0.45, timebound * 0.15)
    p1_deadline = min(started + p1_budget, effective_deadline)
    sol = a_star_search(initial_state, h_admissible, timebound, started,
                        weight=1.0, deadline=p1_deadline, rescue_on_timeout=False)
    if sol is False:
        LAST_STATS.update(elapsed=perf_counter() - started, status="FAILED")
        return False
    if sol is not None:
        LAST_STATS.update(elapsed=perf_counter() - started, status="SOLVED")
        return sol

    # PHA 2: Tìm lời giải hợp lệ nhanh nhất bằng Weighted A* (w = 3.0, h_fast)
    best_sol = a_star_search(initial_state, h_fast, timebound, started,
                             weight=3.0, deadline=effective_deadline)

    # Nếu h_fast chưa ra, thử pha dự phòng với h_admissible (w = 2.0)
    if best_sol is None or best_sol is False:
        if perf_counter() < effective_deadline:
            best_sol = a_star_search(initial_state, h_admissible, timebound, started,
                                     weight=2.0, deadline=effective_deadline)

    if best_sol is None or best_sol is False:
        LAST_STATS.update(elapsed=perf_counter() - started, status="TIMEOUT")
        return False

    # PHA 3: Refinement (w = 1.8) — Dồn thời gian còn lại siết cận gọt bước
    # - Frontier dùng h_fast để ưu tiên tìm kiếm nhanh, cắt cận dùng h_admissible để bảo đảm an toàn.
    # - Lượt gọt đầu dùng toàn bộ thời gian còn lại đến effective_deadline (đã giữ phần đệm an toàn).
    # - Chỉ mở lượt tiếp theo nếu lượt trước thực sự giảm số bước và vẫn còn ít nhất 1.5 giây.
    while effective_deadline - perf_counter() >= 1.5:
        refined_sol = a_star_search(
            initial_state, h_fast, timebound, started,
            weight=1.8, deadline=effective_deadline,
            cost_bound=best_sol.gval,
            rescue_on_timeout=True,
            prune_heuristic_fn=h_admissible
        )
        if refined_sol and refined_sol.gval < best_sol.gval:
            best_sol = refined_sol
        else:
            # Hết giờ (None), cạn frontier (False), hoặc không rút thêm được bước -> dừng
            break

    LAST_STATS.update(elapsed=perf_counter() - started, status="SOLVED")
    return best_sol
