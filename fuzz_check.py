
"""fuzz_check.py - so solver với BFS độc lập trên map ngẫu nhiên nhỏ. KHÔNG nộp file này."""
import random
import sys
import time
from collections import deque
 
import solution
from sokoban import SokobanState, sokoban_goal_state
from validation import validate_solution
 
 
def tao_map(rng):
    w, h = rng.randint(3, 5), rng.randint(3, 4)
    o = [(x, y) for x in range(w) for y in range(h)]
    rng.shuffle(o)
    n_robot, n_box = rng.randint(1, 2), rng.randint(1, 3)
    n_store = n_box + rng.randint(0, 1)
    n_obs = rng.randint(0, 3)
    if n_robot + n_box + n_obs > len(o):
        return None
    robots = [o.pop() for _ in range(n_robot)]
    boxes = [o.pop() for _ in range(n_box)]
    obstacles = [o.pop() for _ in range(n_obs)]
    free = [c for c in o] + boxes            # đích có thể trùng ô thùng
    rng.shuffle(free)
    storage = free[:n_store]
    if len(storage) < n_box:
        return None
    return SokobanState("START", 0, None, w, h, tuple(robots), frozenset(boxes),
                        frozenset(storage), frozenset(obstacles))
 
 
def bfs(s0, gioi_han=400_000):
    """BFS tham chiếu. Trả số bước tối ưu, None nếu vô nghiệm, 'QUA_LON' nếu quá lớn."""
    if sokoban_goal_state(s0):
        return 0
    q, seen = deque([s0]), {s0.hashable_state()}
    while q:
        for c in q.popleft().successors():
            k = c.hashable_state()
            if k in seen:
                continue
            seen.add(k)
            if sokoban_goal_state(c):
                return c.gval
            q.append(c)
        if len(seen) > gioi_han:
            return "QUA_LON"
    return None
 
 
def mo_ta(st):
    return (f"SokobanState('START', 0, None, {st.width}, {st.height}, {st.robots}, "
            f"frozenset({sorted(st.boxes)}), frozenset({sorted(st.storage)}), "
            f"frozenset({sorted(st.obstacles)}))")
 
 
def main(n=500, seed=1):
    rng = random.Random(seed)
    dem = {"khop": 0, "bo_qua": 0}
    loi = []
    t0 = time.time()
    for _ in range(n):
        st = tao_map(rng)
        if st is None:
            continue
        ref = bfs(st)
        if ref == "QUA_LON":
            dem["bo_qua"] += 1
            continue
        try:
            f = solution.solve(st, 10)
        except Exception as e:
            loi.append(("CRASH", type(e).__name__, st))
            continue
        if ref is None:
            if f is not False:
                loi.append(("VÔ NGHIỆM nhưng solver trả nghiệm", f.gval, st))
            else:
                dem["khop"] += 1
        else:
            if f is False:
                loi.append((f"CÓ NGHIỆM ({ref} bước) nhưng solver trả False", None, st))
            else:
                ok, msg = validate_solution(st, f)
                if not ok:
                    loi.append(("LỜI GIẢI SAI", msg, st))
                elif f.gval != ref:
                    loi.append((f"SỐ BƯỚC LỆCH (BFS={ref})", f.gval, st))
                else:
                    dem["khop"] += 1
    print(f"seed={seed}: khớp {dem['khop']}, bỏ qua (quá lớn) {dem['bo_qua']}, LỆCH {len(loi)}  [{time.time() - t0:.0f}s]")
    for loai, chi_tiet, st in loi[:5]:
        print("  >>", loai, "| solver:", chi_tiet)
        print(st.state_string())
        print("  ", mo_ta(st))
    return len(loi)
 
 
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    sys.exit(1 if main(n, seed) else 0)