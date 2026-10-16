import solution
from sokoban import SokobanState


def simple_state(solved=False):
    return SokobanState(
"START", 0, None, 4, 3, ((0, 1),),
frozenset([(2, 1) if solved else (1, 1)]),
frozenset([(2, 1)]), 
frozenset()
)
initial = simple_state()
result = solution.solve(initial, timebound=10)
print("=== TEST 1: BFS ===")
print("Có lời giải:", result is not False)
print("Thống kê:", solution.LAST_STATS)
assert solution.LAST_STATS["expanded"] >= 0
assert solution.LAST_STATS["generated"] >= 0
assert solution.LAST_STATS["unique"] >= 1
assert solution.LAST_STATS["elapsed"] >= 0
if result is not False:
    assert solution.LAST_STATS["status"] == "SOLVED"

result = solution.solve(simple_state(), timebound=0)
print("\n=== TEST 2: TIMEOUT ===")
print("Kết quả là False:", result is False)
print("Thống kê:", solution.LAST_STATS)
assert result is False
assert solution.LAST_STATS["status"] == "TIMEOUT"
print("\nCác kiểm tra thống kê cơ bản đã đạt.")