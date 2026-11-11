# NOTES — Nhật ký dự án Sokoban
## Tuần 1 — ngày họp 09/10/2026
### Đã làm
- Long-13/10/2026 đã mô phỏng BFS bằng tay trên map 4×3 trong public_tests.py và đã rút ra được:
    1. BFS sử dụng hàng đợi FIFO và duyệt trạng thái theo từng mức độ sâu.
    2. Map 4×3: robot (0,1), hộp (1,1), đích (2,1), không có chướng ngại vật.
    3. Từ trạng thái đầu, thứ tự sinh trạng thái hợp lệ là UP, RIGHT, DOWN; LEFT không hợp lệ.
    4. BFS lấy trạng thái đầu ra xét trước, sau đó lấy trạng thái RIGHT có hộp ở đích và dừng.
    5. Kết quả: đường đi RIGHT, chi phí gval = 1, mở rộng 1 trạng thái không phải đích.
 - Long-14/10/2026 sửa file benchmark.py: thêm import collections(line 3), sửa lại in tổng kết (line 75)
### Quyết định và lý do
- Quyt định: ... Vì sao: ... Phương án bị loại: ...


- <H Anh>-16/10/2026  Đã review PR baseline BFS của A (PR #__): đã đọc, tự giải thích được vòng lặp BFS, đã chạy thử trên máy. Câu hỏi để lại: __.
- Đã xây dựng heuristic tổng khoảng cách đẩy để ước lượng số lần đẩy hộp tối thiểu cần thiết nhằm đưa tất cả hộp đến các ô đích (storage).
### Tuần 1 — Thành viên H Anh : Heuristic tổng khoảng cách đẩy

### 1.

Nội dung thực hiện:
- Định nghĩa khoảng cách đẩy giữa hộp và ô đích.
- Xây dựng công thức heuristic tổng khoảng cách đẩy.
- Viết code Python minh họa cách tính heuristic.
- Tính tay heuristic cho bài toán `PROBLEMS[1]`.
- Giải thích ý nghĩa và cách sử dụng heuristic trong tìm kiếm.

### 2. Định nghĩa heuristic tổng khoảng cách đẩy

#### 2.1. Khoảng cách đẩy

Khoảng cách đẩy `d_push(box, goal)` là số lần đẩy ít nhất cần thiết để đưa một hộp từ vị trí hiện tại đến một ô đích.

Khi xét một lần đẩy theo hướng `direction`, cần kiểm tra:

- Vị trí mới của hộp phải nằm trong bản đồ.
- Vị trí mới của hộp không được là tường hoặc chướng ngại vật.
- Robot phải có thể đứng ở ô phía sau hộp để thực hiện thao tác đẩy.
- Hộp chỉ có thể được đẩy, không thể kéo.

Khoảng cách đẩy khác với khoảng cách Manhattan. Khoảng cách Manhattan chỉ dựa trên chênh lệch tọa độ, trong khi khoảng cách đẩy phải xét các hướng đẩy hợp lệ trên bản đồ.

Nếu không tồn tại chuỗi đẩy hợp lệ để đưa hộp đến ô đích, khoảng cách đẩy được xem là vô hạn.

#### 2.2. Công thức heuristic

Gọi:
- `boxes` là tập hợp vị trí các hộp.
- `goals` là tập hợp vị trí các ô đích.
- `d_push(box, goal)` là khoảng cách đẩy tối thiểu từ hộp đến ô đích.

Với nhiều hộp và nhiều ô đích, heuristic tổng khoảng cách đẩy được tính bằng cách ghép mỗi hộp với một ô đích khác nhau sao cho tổng khoảng cách đẩy nhỏ nhất.

```python
h(s) = min(
    sum(d_push(boxes[i], goal_order[i]) for i in range(n))
    for goal_order in permutations(goals)
)
```

Trong đó:
- `s` là trạng thái hiện tại.
- `n` là số hộp.
- `permutations(goals)` tạo ra các cách sắp xếp ô đích để thử các cách ghép hộp–đích.
- Chỉ ghép mỗi hộp với một ô đích và mỗi ô đích với một hộp.
- Chọn tổng khoảng cách đẩy nhỏ nhất trong các cách ghép hợp lệ.

Với trường hợp chỉ có một hộp và một ô đích:

```python
h(s) = d_push(box, goal)
```

Lưu ý: Không nên cộng khoảng cách đến ô đích gần nhất của từng hộp một cách độc lập nếu nhiều hộp có thể cùng chọn một ô đích. Cách ghép một-một giúp tránh tình trạng đó.

### 3. Code Python tính heuristic tổng khoảng cách đẩy

Đoạn code dưới đây tính tổng khoảng cách đẩy nhỏ nhất bằng cách thử các cách ghép hộp với ô đích. Hàm `push_distance` được truyền vào để cung cấp khoảng cách đẩy đã tính trên bản đồ.

```python
from itertools import permutations


def total_push_heuristic(boxes, goals, push_distance):
    """
    Tính heuristic tổng khoảng cách đẩy.

    Args:
        boxes: Danh sách vị trí các hộp.
        goals: Danh sách vị trí các ô đích.
        push_distance: Hàm trả về khoảng cách đẩy tối thiểu
                       từ một hộp đến một ô đích.

    Returns:
        Tổng khoảng cách đẩy nhỏ nhất.
        float('inf') nếu không có cách ghép hợp lệ.
    """
    if len(boxes) != len(goals):
        raise ValueError("Số hộp phải bằng số ô đích.")

    n = len(boxes)

    if n == 0:
        return 0

    min_total = float("inf")

    # Thử tất cả các cách ghép hộp với ô đích.
    for goal_order in permutations(goals):
        total = 0

        for box, goal in zip(boxes, goal_order):
            distance = push_distance(box, goal)

            # Nếu không thể đẩy hộp đến ô đích này,
            # cách ghép hiện tại không hợp lệ.
            if distance == float("inf"):
                total = float("inf")
                break

            total += distance

        min_total = min(min_total, total)

    return min_total
```

#### 3.1. Ví dụ kiểm tra với `PROBLEMS[1]`

Trong `sokoban.py`, `PROBLEMS[1]` là phần tử thứ hai của tuple `PROBLEMS` vì chỉ số trong Python bắt đầu từ `0`.

Dữ liệu của bài toán:
- Vị trí hộp: `(1, 1)`.
- Vị trí ô đích: `(0, 0)`.

Theo cách tính tay ở mục 4, khoảng cách đẩy tối thiểu từ `(1, 1)` đến `(0, 0)` là `2`.

```python
boxes = [(1, 1)]
goals = [(0, 0)]


def push_distance(box, goal):
    # Khoảng cách đẩy đã tính cho PROBLEMS[1].
    known_distances = {
        ((1, 1), (0, 0)): 2
    }

    return known_distances.get(box, {}).get(goal, float("inf")) \
        if False else known_distances.get((box, goal), float("inf"))


h = total_push_heuristic(boxes, goals, push_distance)

print(h)  # Kết quả: 2
```

**Lưu ý:** Hàm `push_distance()` trong ví dụ này sử dụng khoảng cách đã biết để kiểm tra hàm tính tổng. Nó chưa tự tìm đường đẩy trên bản đồ. Khi tích hợp vào chương trình Sokoban, cần thay bằng hàm tính khoảng cách đẩy thực tế, có xét tường, chướng ngại vật và điều kiện đứng phía sau hộp.

### 4. Tính tay heuristic cho `PROBLEMS[1]`

#### 4.1. Dữ liệu bài toán

Theo dữ liệu trong `sokoban.py`, `PROBLEMS[1]` có:

- Chiều rộng bản đồ: `5`.
- Chiều cao bản đồ: `5`.
- Vị trí robot: `(2, 1)` và `(2, 3)`.
- Vị trí hộp: `(1, 1)`.
- Vị trí ô đích: `(0, 0)`.
- Các chướng ngại vật: `(1, 0)`, `(2, 0)`, `(3, 0)`, `(1, 4)`, `(2, 4)`, `(3, 4)`.

Ta có:

```python
boxes = [(1, 1)]
goals = [(0, 0)]
```

Do chỉ có một hộp và một ô đích:

```python
h(s) = d_push((1, 1), (0, 0))
```

#### 4.2. Lần đẩy thứ nhất: Đẩy hộp sang trái

Vị trí ban đầu của hộp:

```python
box = (1, 1)
```

Đẩy hộp sang trái một ô:

```text
(1, 1) -> (0, 1)
```

Để thực hiện lần đẩy này, robot cần đứng ở ô bên phải hộp:

```text
(2, 1)
```

Ô này là vị trí robot ban đầu. Ô `(0, 1)` không phải chướng ngại vật, nên lần đẩy này hợp lệ.

Sau lần đẩy thứ nhất:

```python
box = (0, 1)
```

Số lần đẩy đã thực hiện: `1`.

#### 4.3. Lần đẩy thứ hai: Đẩy hộp lên trên

Hộp hiện tại ở vị trí:

```python
box = (0, 1)
```

Đẩy hộp lên trên một ô:

```text
(0, 1) -> (0, 0)
```

Để thực hiện lần đẩy này, robot cần đứng ở ô phía dưới hộp:

```text
(0, 2)
```

Ô `(0, 2)` có thể tiếp cận qua khu vực đi lại của bản đồ, và ô đích `(0, 0)` không phải chướng ngại vật. Vì vậy, lần đẩy này hợp lệ.

Sau lần đẩy thứ hai, hộp nằm đúng trên ô đích:

```python
box = (0, 0)
```

Số lần đẩy đã thực hiện: `2`.

#### 4.4. Kết quả

Chuỗi đẩy tìm được:

```text
(1, 1) -> (0, 1) -> (0, 0)
```

Có hai lần đẩy để đưa hộp đến ô đích. Do đó:

```python
d_push((1, 1), (0, 0)) = 2
h(PROBLEMS[1]) = 2
```

**Kết luận: Heuristic tổng khoảng cách đẩy của `PROBLEMS[1]` bằng `2`.**

Giá trị này là số lần đẩy hộp ước lượng tối thiểu, không phải tổng số bước di chuyển của robot. Robot có thể cần đi thêm các bước để đến vị trí đứng phía sau hộp trước khi đẩy.

### 5. Ý nghĩa và tính chất của heuristic

#### 5.1. Ý nghĩa

Heuristic tổng khoảng cách đẩy ước lượng số lần đẩy còn cần thiết để đưa các hộp đến ô đích.

Trong thuật toán A*, hàm đánh giá thường có dạng:

```python
f(s) = g(s) + h(s)
```

Trong đó:
- `g(s)` là chi phí thực tế từ trạng thái ban đầu đến trạng thái `s`.
- `h(s)` là chi phí còn lại được ước lượng bằng heuristic.
- `f(s)` được dùng để ưu tiên lựa chọn trạng thái trong quá trình tìm kiếm.

Nếu mỗi hành động di chuyển của robot có chi phí `1`, `g(s)` tính cả bước đi và bước đẩy theo mô hình chương trình, còn heuristic ở đây chỉ ước lượng số lần đẩy còn lại.

#### 5.2. Tính admissible

Heuristic admissible là heuristic không ước lượng cao hơn chi phí tối ưu thực tế để đạt mục tiêu.

Nếu khoảng cách đẩy được tính chính xác theo các lần đẩy hợp lệ và mỗi lần đẩy có chi phí `1`, tổng khoảng cách ghép hộp–đích một-một là một cận dưới cho số bước hành động còn lại, vì robot có thể phải đi thêm để chuẩn bị vị trí đẩy.

Với nhiều hộp, cần ghép hộp với các ô đích khác nhau và tính khoảng cách dựa trên các lần đẩy hợp lệ. Không nên cộng khoảng cách gần nhất của từng hộp một cách độc lập nếu nhiều hộp có thể cùng chọn một ô đích.

Nếu một hộp không thể đến bất kỳ ô đích nào theo các lần đẩy hợp lệ, khoảng cách đẩy của hộp đó là vô hạn. Đây có thể là dấu hiệu của trạng thái bế tắc (deadlock). Khi triển khai, cần xử lý trường hợp này rõ ràng.

### 6. Ghi chú triển khai

- Kiểm tra cấu trúc trạng thái trong `state.py` và dữ liệu bản đồ trong `sokoban.py` trước khi tích hợp heuristic.
- Có thể tính trước khoảng cách đẩy từ các vị trí hộp đến các ô đích để tránh tính lặp lại trong quá trình tìm kiếm.
- Khi tính khoảng cách đẩy, phải xét điều kiện ô đích mới và ô robot cần đứng phía sau hộp.
- Các ô mà hộp không thể đẩy đến bất kỳ ô đích nào có thể được đánh dấu là dead squares, trừ những ô đích hợp lệ.
- Không thay đổi dữ liệu của trạng thái gốc khi tính heuristic.
- Kiểm tra kết quả với `PROBLEMS[1]`; kết quả tính tay là `h = 2`.
- Với bài toán nhỏ, có thể so sánh kết quả tìm kiếm với BFS để kiểm tra tính đúng đắn của lời giải.

### 7. Tóm tắt

Heuristic tổng khoảng cách đẩy ước lượng số lần đẩy hộp tối thiểu cần thiết để đưa tất cả hộp đến các ô đích.

Với `PROBLEMS[1]`:
- Hộp bắt đầu ở `(1, 1)`.
- Ô đích ở `(0, 0)`.
- Đẩy trái đến `(0, 1)`.
- Đẩy lên đến `(0, 0)`.
- Tổng số lần đẩy là `2`.

Vì vậy:

```python
h(PROBLEMS[1]) = 2
```

Đây là giá trị heuristic tính theo số lần đẩy, không bao gồm số bước robot đi để tiếp cận vị trí đẩy.


## Tuần 1 - Thành viên C(Long) - Thống nhất cách đếm node mở rộng; chuẩn bị mẫu bảng số liệu 

### 1. Quy ước đo lường

Để so sánh các thuật toán công bằng, nhóm dùng cùng một quy ước:

- **Expanded nodes (node mở rộng):** số trạng thái hợp lệ được lấy ra khỏi frontier và thực sự được xét để sinh successor. Không tính trạng thái đích nếu thuật toán dừng ngay khi lấy trạng thái đích ra mà không xét successor. Không tính mục frontier lỗi thời/bị bỏ qua do đã có đường đi tốt hơn.
- **Generated nodes (node sinh):** số trạng thái successor được tạo bởi lời gọi `state.successors()`. Chốt cách ghi là tổng số successor được trả về từ các lần gọi `successors()`; chỉ số này có thể gồm trạng thái trùng cấu hình.
- **Unique states (trạng thái duy nhất):** số khóa trạng thái khác nhau (`state.hashable_state()`) đã được phát hiện trong quá trình tìm kiếm, nếu thuật toán có theo dõi chỉ số này.
- **Elapsed time (thời gian chạy):** dùng `time.perf_counter()` để đo thời gian thực thi `solve()`; ghi bằng giây. Khởi tạo test nên nằm ngoài khoảng đo nếu chỉ muốn đo solver.
- **Solution cost / steps:** lấy `final_state.gval` nếu solver trả về trạng thái đích hợp lệ. Nếu `solve()` trả `False`, ghi `No solution / timeout` và để số bước là `—`.
- Chạy các thuật toán trên **cùng test, cùng môi trường và cùng timebound**. Ghi rõ nếu một lần chạy timeout hoặc không tìm được lời giải.
- `StateSpace.n` đếm số đối tượng trạng thái được khởi tạo, **không đồng nghĩa với số node mở rộng**.

> Lưu ý triển khai: `SokobanState.successors()` tự tạo đối tượng trạng thái và gán `parent`, `action`, `gval`. Nếu cần đếm chính xác node sinh/mở rộng, hãy đặt bộ đếm trong thuật toán tìm kiếm; tránh suy ra số node mở rộng từ `StateSpace.n`.

### 2. Bảng kết quả kiểm thử

Điền tên/ID test đúng theo bộ test của nhóm. Để trống ô chưa đo; không tự ước lượng số liệu.

| Test ID / map | Thuật toán | Kết quả (Solved / Failed / Timeout) | Số bước (`gval`) | Node sinh | Node mở rộng | Thời gian (s) | Ghi chú |
|---|---|---|---:|---:|---:|---:|---|
| Public test: one box | BFS | — | — | — | — | — | Test nhỏ để kiểm tra đường đi |
| Public test: initial goal | BFS | — | — | — | — | — | Trạng thái đầu đã là đích |
| Public test: zero budget | BFS | — | — | — | — | — | `timebound=0`, kỳ vọng trả `False` theo API |
| Map 4×3 (public test) | BFS | — | — | — | — | — | Dùng để mô phỏng BFS bằng tay |
| Map 4×3 (public test) | A* | — | — | — | — | — | Chỉ điền sau khi A* được triển khai |

#### Quy trình chạy mỗi test

1. Tạo trạng thái đầu mới cho từng lần chạy; không tái sử dụng trạng thái đã bị thay đổi.
2. Ghi thời điểm bắt đầu bằng `time.perf_counter()`.
3. Gọi `solve(initial_state, timebound=...)`, rồi đo thời gian kết thúc.
4. Kiểm tra kết quả bằng validator của framework trước khi ghi `Solved`.
5. Ghi `gval`, node sinh, node mở rộng và thời gian. Ghi `Timeout`/`Failed` rõ ràng thay vì bỏ dòng đó.
6. Với benchmark so sánh, chạy cùng một test nhiều lần nếu có thể và ghi cách tổng hợp (ví dụ: thời gian trung vị); không trộn kết quả chạy có profiling với thời gian benchmark thông thường.

### 3. Profiling bằng cProfile

| Lần chạy | Test ID / map | Thuật toán | Hàm tốn thời gian (theo `cumtime`) | `ncalls` | `tottime` (s) | `cumtime` (s) | Nhận xét / bước tiếp theo |
|---|---|---|---:|---:|---:|---:|---|
| 1 | — | — | — | — | — | — | — |

- `ncalls`: số lần gọi hàm.
- `tottime`: thời gian trong thân hàm, không tính thời gian ở các hàm con.
- `cumtime`: thời gian tích lũy của hàm, bao gồm các lời gọi con.
- Xem các hàm có `cumtime` cao để tìm nơi cần điều tra; số lần gọi lớn tự nó chưa chứng minh hàm là nút thắt.
- `cProfile` tạo thêm overhead. Dùng nó để tìm nút thắt; dùng `time.perf_counter()` trong lần chạy không profiling để báo cáo thời gian benchmark.

### 4. Kiểm chứng tính đúng đắn

| Test ID / map | Validator pass? | Trạng thái đầu không bị sửa? | Parent/action/gval hợp lệ? | Ghi chú |
|---|---|---|---|---|
| Public test: one box | — | — | — | — |
| Public test: initial goal | — | — | — | — |
| Public test: zero budget | — | — | — | — |

### 5. Việc cần hoàn thành trong tuần 1

- [ ] Nhóm thống nhất định nghĩa node sinh và node mở rộng.
- [ ] Mô phỏng BFS bằng tay trên map 4×3; ghi lại thứ tự xét node.
- [ ] Tạo cách đo thời gian bằng `time.perf_counter()`.
- [ ] Chuẩn bị script profiling bằng `cProfile` sau khi có solver chạy được.
- [ ] Chạy public tests và ghi kết quả thực tế vào bảng.
- [ ] Không kết luận A* tốt hơn BFS chỉ từ một test; so sánh trên cùng các map và cùng quy ước đếm.
## Thành viên C - Thống kê BFS và kiểm thử PROBLEMS (16/10/2026)

### Triển khai trong bản làm việc
- `solution.py`: dùng `time.perf_counter()` để đo thời gian bên trong `solve()`; giữ nguyên chữ ký `solve(initial_state, timebound=120)`.
- Bổ sung `LAST_STATS`: `expanded` (node lấy khỏi queue và gọi `successors()`), `generated` (tổng số successor trả về), `unique` (số khóa cấu hình duy nhất được phát hiện), `elapsed` và `status`.
- Quy ước goal-on-generation vẫn được giữ: node đích được trả về ngay khi sinh; vì thế không tính node đích là expanded.
- `benchmark.py`: in thêm các cột expanded/generated/unique; vẫn xác thực lời giải bằng `validation.py`.
- Thêm `profile_solver.py` để xem 20 hàm có `cumtime` cao nhất bằng `cProfile`. Thời gian có profiling không dùng làm số benchmark chính thức.

### Test tích hợp bộ đếm số node mở rộng và thời gian chạy BFS
- Lệnh: `python -m unittest public_tests.py`, `python test_stats.py`

- Kết quả: **3 tests passed** (`one_box`, `initial_goal`, `zero_budget`).
            
            === TEST 1: BFS ===
            Có lời giải: True
            Thống kê: {'expanded': 1, 'generated': 3, 'unique': 3, 'elapsed': 4.55999997939216e-05, 'status': 'SOLVED'}

            === TEST 2: TIMEOUT ===
            Kết quả là False: True
            Thống kê: {'expanded': 0, 'generated': 0, 'unique': 0, 'elapsed': 1.0999992809956893e-06, 'status': 'TIMEOUT'}

### Kết quả BFS trên `sokoban.PROBLEMS`
- Lệnh chạy: `python benchmark.py --timebound 5` (Lệnh này chạy các map từ 0 đến 19, mỗi map có ngân sách 5 giây.)
Chạy trong cùng môi trường Python, `timebound=0.1` giây/map. Đây là lần chạy thử nhanh để kiểm tra thống kê, **không phải kết luận hiệu năng cuối cùng**. Các map `TIMEOUT` chưa tìm được lời giải trong ngân sách này.

| Map | Status  | Steps | Expanded | Generated | Unique | Time (s) | Valid |
|-----|---------|------:|---------:|----------:|-------:|---------:|-------|
| 0   | SOLVED  | 16    | 38626    | 188680    | 51917  | 0.625    | True  |
| 1   | SOLVED  | 4     | 56       | 319       | 127    | 0.001    | True  |
| 2   | SOLVED  | 21    | 4136     | 10887     | 4629   | 0.037    | True  |
| 3   | SOLVED  | 10    | 6458     | 40280     | 10875  | 0.155    | True  |
| 4   | SOLVED  | 8     | 928      | 5877      | 1498   | 0.022    | True  |
| 5   | SOLVED  | 30    | 128745   | 604658    | 142407 | 2.064    | True  |
| 6   | SOLVED  | 16    | 5593     | 27433     | 7319   | 0.113    | True  |
| 7   | SOLVED  | 41    | 2308     | 5652      | 2346   | 0.016    | True  |
| 8   | TIMEOUT | None  | 172852   | 1578971   | 400053 | 5.404    | -     |
| 9   | TIMEOUT | None  | 118700   | 1352690   | 352767 | 5.272    | -     |
| 10  | TIMEOUT | None  | 173374   | 1549503   | 400185 | 5.349    | -     |
| 11  | TIMEOUT | None  | 182300   | 1656996   | 381977 | 5.222    | -     |
| 12  | TIMEOUT | None  | 181044   | 1663570   | 378601 | 5.204    | -     |
| 13  | TIMEOUT | None  | 242682   | 1581409   | 405123 | 5.219    | -     |
| 14  | TIMEOUT | None  | 236291   | 1529016   | 402148 | 5.616    | -     |
| 15  | TIMEOUT | None  | 154170   | 1527962   | 341112 | 5.224    | -     |
| 16  | TIMEOUT | None  | 168059   | 1700605   | 358189 | 5.255    | -     |
| 17  | TIMEOUT | None  | 154848   | 1546465   | 328564 | 5.516    | -     |
| 18  | TIMEOUT | None  | 158796   | 1586552   | 346430 | 5.275    | -     |
| 19  | TIMEOUT | None  | 154569   | 1537123   | 326848 | 5.224    | -     |

**Tổng kết:**
- SOLVED = 8
- TIMEOUT = 12

**Lưu ý về timeout:** kiểm tra deadline được thực hiện giữa các lần mở rộng. Một lần gọi `successors()` có thể tốn nhiều thời gian, nên thời gian thực tế đôi khi vượt `timebound` (đặc biệt map 5). Đây là điểm cần ghi nhận khi tối ưu tiếp; không được hiểu timeout 0.1 giây là giới hạn cứng tuyệt đối.

### Nhận xét
- 8/20 map được giải trong lần chạy nhanh này; cả 7 lời giải đều qua validator.
- BFS vẫn phù hợp làm baseline đúng đắn nhưng tăng số trạng thái nhanh trên các map khó; cần benchmark lại với ngân sách dài hơn và so sánh A* trên cùng map.
- Từ map 8-19 vẫn TIMEOUT thì đó là kết quả phản ánh giới hạn tìm kiếm của BFS trong ngân sách hiện tại, không còn là lỗi ghi trạng thái như trước. 
- `StateSpace.n` không được dùng thay cho `expanded`: nó đếm số đối tượng trạng thái được khởi tạo.


### Việc tuần sau (người - hạn)
- Tuần 2: A (Tuấn) và B (Hải Anh) hoàn thành A* và Heuristic h1 theo biên bản thiết kế bên dưới.

## Tuần 2 — Thống nhất thiết kế giữa A và B: A* và Heuristic Admissible
**Ngày cập nhật:** 19/10/2026 (Họp kỹ thuật Thứ 2)  
**Thành viên tham gia:** Người A (Hồ Anh Tuấn) và Người B (Nghiêm Nguyễn Hải Anh)

### 1. Mục tiêu và Nguyên tắc làm việc
- **Mục tiêu:** Nâng cấp baseline từ BFS lên A* để tìm lời giải tối ưu (số bước bằng BFS) nhưng giảm mạnh số lượng node mở rộng; kiểm chứng đúng đắn trên 8 map đầu tiên (PROBLEMS[0..7]).
- **Làm việc song song, không nghẽn:** A viết khung A* với heuristic mặc định h = 0. B viết hàm ô chết và khoảng cách độc lập, kiểm tra bằng script riêng.
- **Phân chia vùng code trong solution.py (Tránh conflict):**
  - **B phụ trách:** Vùng 2 (Ô chết và bảng khoảng cách) & Vùng 3 (Các hàm Heuristic).
  - **A phụ trách:** Vùng 4 (Thuật toán A*) & Vùng 5 (Hàm solve() và quản lý thời gian).
- **Quy ước nhánh Git:**
  - Nhánh của A: feature/astar-tuan
  - Nhánh của B: feature/dead-squares-HaiAnh
  - Nhánh tích hợp chung (Thứ 5): feature/tich-hop-h1

---

### 2. Biên bản 8 điểm thống nhất kỹ thuật (Giao diện giữa A và B)

1. **Chữ ký hàm và Cơ chế tính trước (Precompute):**
   - B cung cấp hàm make_heuristic(initial_state) trả về một hàm closure h(s) -> int.
   - Bảng khoảng cách và danh sách ô chết được tính **đúng 1 lần duy nhất** ở đầu hàm solve(). Trong vòng lặp A*, A chỉ cần gọi h(s) để tra cứu nhanh O(1).
2. **Quy ước vô nghiệm và Ô chết (Dead squares):**
   - Khai báo hằng số INF = 10**9 ở Vùng 3.
   - Nếu bất kỳ thùng nào rơi vào ô chết hoặc không thể đến đích, h(s) trả về giá trị >= INF.
   - Phía A: Bỏ qua ngay lập tức mọi node con có h >= INF (cắt tỉa nhánh chết, không đẩy vào hàng đợi).
3. **Cắt trạng thái ban đầu:**
   - Nếu trạng thái xuất phát (initial_state) có h >= INF, hàm solve() trả về False ngay lập tức mà không cần khởi động tìm kiếm.
4. **An toàn dữ liệu:**
   - Hàm h(s) chỉ đọc vị trí các thùng (s.boxes), không xét vị trí 
obots, và tuyệt đối **không làm biến đổi (read-only)** đối tượng trạng thái s.
5. **Cơ chế Cache:**
   - Bảng nhớ tạm (cache) của heuristic được đặt trong phạm vi closure, sử dụng khóa là cấu hình thùng s.boxes, không dùng biến toàn cục ngoài module.
6. **Chuẩn thuật toán A* của A:**
   - **Goal test khi pop:** Chỉ kiểm tra trạng thái đích khi lấy node ra khỏi hàng đợi ưu tiên heapq (không kiểm tra khi sinh con như BFS).
   - **Bộ đếm tie-break:** Hàng đợi lưu tuple (f, tie_counter, state) để tránh lỗi so sánh trực tiếp giữa hai đối tượng SokobanState khi có cùng giá trị f.
   - **Quản lý thời gian:** Kiểm tra perf_counter() >= deadline ở đầu mỗi vòng lặp while heap.
7. **Bài kiểm tra đối chứng chung (h = 0):**
   - Khi chạy A* với h = 0, số bước tìm được của A* **phải bằng chính xác 100% số bước của BFS** trên các map giải được trong tuần 1:
     - Map 0: 16 bước | Map 1: 4 bước | Map 2: 21 bước | Map 3: 10 bước
     - Map 4: 8 bước  | Map 5: 30 bước | Map 6: 16 bước | Map 7: 41 bước
8. **Kế hoạch bàn giao và Review chéo:**
   - Thứ 4: A mở PR cho A* (h = 0); B mở PR cho Ô chết và Bảng khoảng cách.
   - Review chéo: B review PR của A, C review PR của B theo đúng quy định sổ tay.
   - Thứ 5: A và B cùng ngồi ghép h1 vào A* trên nhánh tích hợp.
## Tuần 2 - Thành viên C(Long) – HIỆU NĂNG VÀ KIỂM CHỨNG TỐI ƯU

### 1. Mục tiêu thực hiện

Nhiệm vụ của thành viên C trong tuần 2:

- Kiểm tra tính đúng đắn của framework sau khi chỉnh sửa.
- Đo lường hiệu năng thuật toán A*.
- Thống kê số node mở rộng, số node được sinh và số trạng thái duy nhất.
- Sử dụng `cProfile` để xác định các hàm tiêu tốn nhiều thời gian.
- Tối ưu cấu trúc dữ liệu nhằm giảm chi phí xử lý.
- So sánh hiệu năng trước và sau tối ưu.

### 2. Kiểm thử tính đúng đắn của framework

Sau khi chỉnh sửa file `sokoban.py`, tiến hành kiểm thử bằng lệnh:

```bash
python -m unittest test_framework
```

**Kết quả:** Các test trong `test_framework` đều PASS (7/7).

Điều này xác nhận các chức năng cơ bản của framework vẫn hoạt động đúng sau khi tối ưu:

- Robot di chuyển đúng quy tắc.
- Kiểm tra va chạm giữa robot, hộp và vật cản.
- Robot đẩy hộp đúng quy tắc.
- Trạng thái mới được tạo chính xác.
- Các trạng thái cũ không bị thay đổi ngoài ý muốn.

### 3. Tối ưu cấu trúc dữ liệu `new_boxes`

#### 3.1. Vấn đề trong phiên bản ban đầu

Trong hàm `successors()` của lớp `SokobanState`, mỗi lần xét một hướng di chuyển, chương trình đều tạo một bản sao của tập hợp hộp:

```python
new_boxes = set(self.boxes)
```

Tuy nhiên, phần lớn các bước di chuyển của robot không làm thay đổi vị trí hộp.

Việc liên tục tạo bản sao không cần thiết gây ra chi phí xử lý và cấp phát bộ nhớ.

#### 3.2. Giải pháp tối ưu

Thay vì luôn tạo bản sao, phiên bản mới sử dụng lại tập hợp `self.boxes`:

```python
new_boxes = self.boxes
```

Chỉ khi robot thực sự đẩy hộp, chương trình mới tạo một bản sao để cập nhật:

```python
new_boxes = set(self.boxes)
new_boxes.remove(new_location)
new_boxes.add(new_box_location)
new_boxes = frozenset(new_boxes)
```

#### 3.3. Nguyên lý tối ưu

- `self.boxes` có kiểu `frozenset`, là tập hợp bất biến.
- Khi robot di chuyển mà không đẩy hộp, trạng thái mới có thể dùng chung tập hợp hộp với trạng thái cũ.
- Khi robot đẩy hộp, chương trình tạo một tập hợp mới, cập nhật vị trí hộp rồi chuyển về `frozenset`.
- Không làm thay đổi dữ liệu hộp của trạng thái ban đầu.

**Kết quả:** Giảm số lần sao chép tập hợp hộp khi sinh trạng thái kế tiếp, đồng thời giữ nguyên logic di chuyển của Sokoban.

### 4. Đo lường và so sánh hiệu năng

#### 4.1. Công cụ đo

Sử dụng chương trình `benchmark_astar.py` để đo hiệu năng thuật toán A*.

Lệnh thực hiện:

```bash
python benchmark_astar.py --maps 0 14 --timebound 30
```

Hai bản đồ được lựa chọn:

- Map 0: Bản đồ có độ phức tạp tương đối thấp.
- Map 14: Bản đồ có độ phức tạp cao hơn, giúp đánh giá hiệu năng khi phải xử lý nhiều trạng thái.

Mỗi bản đồ được chạy 3 lần sau tối ưu để tính thời gian trung bình.

#### 4.2. Các chỉ số đánh giá

| Chỉ số | Ý nghĩa |
|---|---|
| Steps | Số bước trong lời giải |
| Expanded | Số node đã được mở rộng |
| Generated | Tổng số node được sinh ra |
| Unique | Số trạng thái duy nhất |
| Time(s) | Thời gian thực thi |
| Valid | Lời giải có hợp lệ hay không |

#### 4.3. Kết quả sau tối ưu

Kết quả của 3 lần chạy:

| Map | Lần 1 (s) | Lần 2 (s) | Lần 3 (s) | Trung bình (s) |
|---|---:|---:|---:|---:|
| 0 | 0.142 | 0.139 | 0.149 | **0.143** |
| 14 | 5.972 | 5.952 | 6.114 | **6.013** |

Các chỉ số node trong cả 3 lần chạy đều giống nhau:

| Map | Steps | Expanded | Generated | Unique | Valid |
|---|---:|---:|---:|---:|---|
| 0 | 16 | 9,517 | 47,952 | 14,182 | True |
| 14 | 25 | 274,308 | 1,763,445 | 422,515 | True |

#### 4.4. So sánh thời gian trước và sau tối ưu

Dữ liệu đo trước tối ưu:

| Map | Thời gian trước tối ưu (s) |
|---|---:|
| 0 | 0.170 |
| 14 | 7.621 |

So sánh với thời gian trung bình sau tối ưu:

| Map | Trước tối ưu (s) | Sau tối ưu (s) | Mức giảm |
|---|---:|---:|---:|
| 0 | 0.170 | 0.143 | 15.7% |
| 14 | 7.621 | 6.013 | 21.1% |

Công thức tính:

\[
\text{Mức giảm}=
\frac{T_{\text{trước}}-T_{\text{sau}}}
{T_{\text{trước}}}\times100\%
\]

**Nhận xét:**

- Thời gian thực thi giảm ở cả hai bản đồ.
- Map 0 giảm khoảng 15.7%.
- Map 14 giảm khoảng 21.1%.
- Các lần chạy sau tối ưu cho kết quả ổn định, với số node và số bước giống nhau.

Lưu ý: Thời gian trước tối ưu hiện được ghi nhận từ một lần chạy, trong khi thời gian sau tối ưu là trung bình của ba lần chạy. Vì vậy, mức cải thiện trên mang tính tham khảo; cần đo nhiều lần ở cả hai phiên bản nếu muốn có phép so sánh thực nghiệm cân bằng hơn.

**Lưu ý về số node:** Số liệu Expanded, Generated và Unique trước tối ưu cần được bổ sung từ log benchmark phiên bản cũ. Không sử dụng số liệu từ những lần chạy A* có cấu hình hoặc phiên bản heuristic khác nhau để so sánh trực tiếp.

### 5. Phân tích hiệu năng bằng cProfile

Sử dụng công cụ `cProfile` để xác định các hàm tiêu tốn nhiều thời gian trong quá trình giải Sokoban.

Các lệnh đã sử dụng:

```bash
python profile_solver.py --map 0 --timebound 30
python profile_solver.py --map 14 --timebound 30
```

Kết quả profiling cho thấy:

- `a_star_search()` là hàm điều khiển quá trình tìm kiếm.
- `successors()` có thời gian thực thi tích lũy đáng kể.
- `SokobanState.__init__()` được gọi nhiều lần do quá trình sinh trạng thái.
- Các thao tác xử lý tập hợp và kiểm tra trạng thái cũng góp phần vào chi phí tính toán.

**Nhận xét:** Hàm `successors()` là một trong những vị trí đáng chú ý để tối ưu vì được gọi với tần suất cao trong quá trình tìm kiếm.

Việc hạn chế tạo bản sao `new_boxes` không cần thiết là một cải tiến phù hợp với kết quả phân tích này.

### 6. Kết luận

Trong tuần 2, thành viên C đã thực hiện:

- Kiểm thử framework sau khi chỉnh sửa và xác nhận 7/7 test PASS.
- Phân tích hiệu năng thuật toán A* bằng benchmark.
- Sử dụng `cProfile` để xác định các hàm tiêu tốn nhiều thời gian.
- Tối ưu việc tạo bản sao tập hợp `new_boxes` trong `successors()`.
- Chạy benchmark 3 lần sau tối ưu trên Map 0 và Map 14.
- Ghi nhận thời gian chạy trung bình giảm khoảng 15.7% trên Map 0 và 21.1% trên Map 14 so với số liệu trước tối ưu đã có.

**Đánh giá:** Cải tiến `new_boxes` giúp giảm chi phí xử lý khi sinh trạng thái mà không thay đổi quy tắc hoạt động của Sokoban.
### 7 . Tối ưu A* bằng chiến lược Tie-break theo h

#### 7.1. Mục tiêu

Cải thiện hiệu năng thuật toán A* bằng cách thay đổi chiến lược lựa chọn trạng thái khi có nhiều trạng thái cùng giá trị hàm đánh giá `f`.

Giữ nguyên heuristic, cách sinh trạng thái và logic tìm kiếm; chỉ thay đổi thứ tự ưu tiên trong hàng đợi `frontier`.

#### 7.2. Hai chiến lược được so sánh

**Phiên bản 1: A* FIFO (`solution.py`)**

Sử dụng tuple:

```python
(f, counter, state)
```

- Ưu tiên trạng thái có `f = g + h` nhỏ nhất.
- Nếu hai trạng thái có cùng `f`, ưu tiên trạng thái được đưa vào hàng đợi trước.
- `counter` đảm bảo không phải so sánh trực tiếp các đối tượng trạng thái.

**Phiên bản 2: A* Tie-break theo h (`solution_fifo.py`)**

Thay đổi tuple thành:

```python
(f, h, counter, state)
```

Các vị trí được sửa trong hàm `a_star_search()`:

```python
# Đưa trạng thái ban đầu vào frontier
heapq.heappush(
    frontier,
    (f_init, h_init, next(tie_counter), initial_state)
)

# Lấy trạng thái ra khỏi frontier
f_val, h_val, _, current = heapq.heappop(frontier)

# Đưa trạng thái kế tiếp vào frontier
heapq.heappush(
    frontier,
    (f_child, h_val, next(tie_counter), child)
)
```

**Nguyên lý hoạt động:**

1. Ưu tiên trạng thái có `f` nhỏ nhất.
2. Nếu hai trạng thái có cùng `f`, ưu tiên trạng thái có `h` nhỏ hơn.
3. Nếu cả `f` và `h` đều bằng nhau, sử dụng `counter` để duy trì thứ tự FIFO.

Do `f` vẫn là tiêu chí ưu tiên đầu tiên nên tie-break chỉ thay đổi thứ tự xử lý giữa các trạng thái có cùng `f`.

#### 7.3. Chuẩn bị benchmark

Các file sử dụng:

| File | Chức năng |
|---|---|
| `solution.py` | A* FIFO ban đầu |
| `solution_fifo.py` | A* tie-break theo h |
| `benchmark_astar.py` | Benchmark phiên bản FIFO |
| `benchmark_astar_tiebreak.py` | Benchmark phiên bản tie-break |

Trong `benchmark_astar_tiebreak.py`, đổi import thành:

```python
import solution_fifo as solution
```

Các điều kiện thử nghiệm:
- Cùng heuristic và logic tìm kiếm.
- Cùng bản đồ.
- Cùng giới hạn thời gian 30 giây.
- Mỗi phiên bản chạy 3 lần.
- Sử dụng Map 0 và Map 14 để so sánh.

#### 7.4. Kết quả benchmark

Số liệu dưới đây là kết quả của 3 lần chạy. Thời gian được tính trung bình.

**Map 0**

| Chỉ số | A* FIFO | Tie-break h |
|---|---:|---:|
| Status | SOLVED | SOLVED |
| Steps | 16 | 16 |
| Expanded | 9.517 | 6.435 |
| Generated | 47.952 | 32.581 |
| Unique | 14.182 | 9.910 |
| Time trung bình | 0,182 s | 0,115 s |
| Valid | True | True |

**Map 14**

| Chỉ số | A* FIFO | Tie-break h |
|---|---:|---:|
| Status | SOLVED | SOLVED |
| Steps | 25 | 25 |
| Expanded | 274.308 | 171.406 |
| Generated | 1.763.445 | 1.102.430 |
| Unique | 422.515 | 283.772 |
| Time trung bình | 8,267 s | 3,713 s |
| Valid | True | True |

#### 7.5. Tỷ lệ cải thiện

| Chỉ số | Map 0 | Map 14 |
|---|---:|---:|
| Expanded giảm | 32,4% | 37,5% |
| Generated giảm | 32,1% | 37,5% |
| Unique giảm | 30,1% | 32,8% |
| Thời gian giảm | 36,7% | 55,1% |

Công thức tính tỷ lệ giảm:

\[
\text{Reduction} =
\frac{\text{FIFO} - \text{Tie-break}}
{\text{FIFO}}\times 100\%
\]

#### 7.6. Kiểm chứng tính đúng đắn

- Cả hai phiên bản đều tìm được lời giải trên Map 0 và Map 14.
- Tất cả kết quả đều có `Valid = True`.
- Số bước lời giải của hai phiên bản giống nhau:
  - Map 0: 16 bước.
  - Map 14: 25 bước.
- Hai lệnh kiểm tra framework và thống kê đều chạy thành công:
  - `python -m unittest test_framework`
  - `python test_stats.py`

Lưu ý: Kết quả trên hai bản đồ là bằng chứng thực nghiệm cho các trường hợp đã thử nghiệm, không thay thế chứng minh tính tối ưu trên mọi bản đồ. Tính tối ưu còn phụ thuộc vào tính chất của heuristic và điều kiện của thuật toán A*.

#### 7.7. Kết luận

Chiến lược tie-break theo `h` cho kết quả tốt hơn FIFO trong hai bản đồ thử nghiệm.

- Giảm số node mở rộng từ 32,4% đến 37,5%.
- Giảm thời gian chạy từ 36,7% đến 55,1%.
- Giữ nguyên số bước lời giải và tính hợp lệ của kết quả.

Vì vậy, tie-break theo `h` là một cải tiến đáng giữ lại và tiếp tục đánh giá trên nhiều bản đồ hơn.

**Vai trò Member C:** Thực hiện thay đổi chiến lược tie-break, xây dựng benchmark riêng, kiểm chứng kết quả và phân tích mức cải thiện hiệu năng.


## TUẦN 3:

## Tuần 3 — Hải Anh (B): h_admissible, h_fast và ô chết khối 2x2

### Đã làm
- `solution.py` Vùng 3: thêm `tinh_bang_di_bo`, `lam_ham_khoi_2x2`, `make_heuristics`.
- `make_heuristics(initial_state)` trả về cặp `(h_admissible, h_fast)`, bảng tính 1 lần, không dùng biến toàn cục.
- Nhánh: `feature/heuristic-walk-HaiAnh`. Reviewer: C. Hải Anh review PR Weighted A* của A.

### Thiết kế (giao diện với A)
- `h_admissible(s)` = h2 (ghép cặp bitmask) + cắt khối 2x2. Dùng ở pha w = 1.
- `h_fast(s)` = `h_admissible(s)` + `buoc_di_bo(s)`. Dùng ở các pha w > 1.
- Cả hai trả về >= INF khi bế tắc; A bỏ qua node có h >= INF như đã thống nhất Tuần 2.
- `buoc_di_bo(s)` = min theo (robot, thùng chưa ở đích, ô kề thùng) của khoảng cách đi bộ,
  tính bằng bảng BFS bỏ qua thùng và robot (chỉ xét tường) nên là cận dưới của đi bộ thật.

### Ô chết khối 2x2
- Bế tắc khi cả 4 ô của một khối 2x2 là tường / ngoài bàn / thùng và có ít nhất 1 thùng chưa ở đích.
- Khối toàn thùng đã ở đích thì KHÔNG bế tắc (đã unit test).
- Robot không tính là vật chặn vì robot di chuyển được.
- Đây là bế tắc thật (trạng thái vô nghiệm) nên cắt không làm mất lời giải tối ưu, dùng được ở cả pha w = 1.

### Lập luận admissible
- `h_admissible` = h2 (admissible, đã chứng minh Tuần 2) + cắt bế tắc thật => vẫn admissible.
- `h_fast` KHÔNG được đảm bảo admissible. Số bước đi bộ trước lần đẩy đầu tiên của một thùng chưa ở đích
  luôn >= `buoc_di_bo`, nhưng các bước đó có thể là lần đẩy một thùng đã ở đích mà h2 đã đếm
  (ví dụ h2 ghép thùng đã ở đích sang đích khác rẻ hơn). Khi đó cộng thêm đi bộ là đếm trùng.
- Thực nghiệm: [ĐIỀN số map ngẫu nhiên đã thử và số lần vi phạm của h_fast, nếu bạn chạy; nếu không chạy thì xóa dòng này].
- Kết luận: chưa chứng minh được h_fast admissible => chỉ dùng ở w > 1, pha cuối w = 1 dùng h_admissible.
- Hệ quả nếu h quá cao: A* có thể bỏ qua đường tốt hơn và trả lời giải kém tối ưu.

### Kết quả benchmark (chạy bằng `python scratch_b_tuan3.py`, máy của Hải Anh)

**Pha w = 1:** số bước A* với h_admissible bằng BFS trên cả 8 map (OK). Khối 2x2 giảm node ở 4/8 map.

| Map | BFS (bước) | node h2 cũ | node h_admissible (có 2x2) | node h_admissible (không 2x2) | Giảm nhờ 2x2 |
|---|---:|---:|---:|---:|---:|
| 0 | 16 | 9516 | 9016 | 9516 | 5,3% |
| 1 | 4 | 39 | 39 | 39 | 0% |
| 2 | 21 | 2044 | 1516 | 2044 | 25,8% |
| 3 | 10 | 873 | 873 | 873 | 0% |
| 4 | 8 | 349 | 349 | 349 | 0% |
| 5 | 30 | 15023 | 13477 | 15023 | 10,3% |
| 6 | 16 | 739 | 739 | 739 | 0% |
| 7 | 41 | 1088 | 848 | 1088 | 22,1% |

**Pha w = 3, h2 so với h_fast** (bước / node mở rộng / giây):

| Map | BFS | h2 | h_fast |
|---|---:|---|---|
| 0 | 16 | 16 / 202 / 0,046 | 17 / 158 / 0,046 |
| 1 | 4 | 4 / 14 / 0,003 | 5 / 16 / 0,005 |
| 2 | 21 | 21 / 195 / 0,030 | 21 / 268 / 0,047 |
| 3 | 10 | 10 / 163 / 0,045 | 10 / 259 / 0,075 |
| 4 | 8 | 9 / 118 / 0,028 | 9 / 111 / 0,030 |
| 5 | 30 | 30 / 269 / 0,050 | 30 / 234 / 0,058 |
| 6 | 16 | 20 / 173 / 0,035 | 20 / 107 / 0,028 |
| 7 | 41 | 41 / 439 / 0,054 | 41 / 646 / 0,088 |

- Thời gian mỗi lần gọi heuristic (map 15, 5000 trạng thái): h_admissible 56,2 µs; h_fast 91,1 µs (chậm hơn khoảng 1,6 lần).
- Nhận xét map nhỏ (0..7): h_fast mở rộng ít node hơn ở map 0, 4, 5, 6 nhưng nhiều node hơn ở map 1, 2, 3, 7;
  lời giải dài thêm 1 bước ở map 0 và 1. Trên map nhỏ h_fast không cho lợi ích rõ ràng.
- **Map lớn 8..19, pha w = 3, mỗi map 10 giây** (bước / node mở rộng / giây):

| Map | h2 | h_fast | Nhận xét |
|---|---|---|---|
| 8 | 14 / 86 / 0,04 | 14 / 236 / 0,23 | h_fast mở rộng nhiều node hơn |
| 9 | 24 / 139 / 0,16 | 25 / 501 / 0,40 | nhiều node hơn, dài thêm 1 bước |
| 10 | 37 / 750 / 0,33 | 36 / 1162 / 0,64 | nhiều node hơn, ngắn hơn 1 bước |
| 11 | 30 / 374 / 0,15 | 31 / 395 / 0,21 | gần như hòa, dài thêm 1 bước |
| 12 | 26 / 1361 / 0,50 | 26 / 660 / 0,38 | node giảm khoảng 2 lần |
| 13 | 29 / 282 / 0,08 | 29 / 168 / 0,06 | node giảm |
| 14 | 27 / 626 / 0,15 | 27 / 316 / 0,10 | node giảm khoảng 2 lần |
| 15 | 72 / 17199 / 5,40 | 74 / 3534 / 1,81 | node giảm khoảng 4,9 lần, thời gian giảm khoảng 3 lần, dài thêm 2 bước |
| 16 | 56 / 16527 / 5,37 | 58 / 4006 / 1,87 | node giảm khoảng 4,1 lần, thời gian giảm khoảng 2,9 lần, dài thêm 2 bước |
| 17 | TIMEOUT / 30073 / 10,00 | TIMEOUT / 20511 / 10,00 | cả hai chưa giải trong 10 giây trên máy này |
| 18 | TIMEOUT / 27551 / 10,00 | TIMEOUT / 22002 / 10,00 | cả hai chưa giải trong 10 giây trên máy này |
| 19 | 78 / 5443 / 1,78 | 78 / 3756 / 2,03 | node giảm khoảng 1,4 lần nhưng thời gian chậm hơn nhẹ |

- Tổng: cả hai heuristic đều giải được 10/12 map lớn trong 10 giây trên máy của Hải Anh.
- h_fast có lợi rõ ở các map khó vừa (12, 13, 14, 15, 16): ít node hơn và nhanh hơn ở map 15, 16.
- h_fast làm tệ ở các map dễ (8, 9, 10): mở rộng nhiều node hơn, vì thành phần đi bộ làm lệch thứ tự ưu tiên.
- Kết luận tạm: h_fast đáng giữ cho pha w > 1 vì lợi ở map khó lớn hơn thiệt ở map dễ,
  nhưng đổi lại có thể dài thêm 1-2 bước ở pha này; pha w = 1 sẽ cải thiện lại nếu còn thời gian.
- Đánh đổi: h_fast tốn thêm thời gian mỗi lần gọi; chỉ đáng dùng nếu giảm đủ node ở map khó.
  Quyết định giữ hay bỏ sẽ chốt ở họp Chủ nhật dựa trên bảng map lớn.

### Quyết định và lý do
- Giữ khối 2x2 trong cả hai hàm vì là bế tắc thật và giảm node ở một số map.
- Phương án bị loại: cộng bước đi bộ cho TỪNG thùng (đếm trùng nặng, dễ vượt chi phí thật).
- Phương án bị loại: BFS đi bộ có tính thùng làm vật cản mỗi lần gọi h (quá chậm).




## Tuần 3 — Tuấn (A): Weighted A*, Anytime Search và Giải trọn vẹn 20/20 Maps

### 1. Mục tiêu và Thiết kế (Vùng 4 & 5 trong solution.py)
- **Weighted A\*:** Đánh đổi tính tối ưu lấy tốc độ tìm kiếm để mở khóa các map lớn (Maps 9–19):
  $$f(s) = g(s) + w \times h(s)$$
  với $w \ge 1.0$.
- **Kế thừa Tie-breaking theo h (từ kiểm chứng của Long - C):**
  Hàng đợi ưu tiên lưu tuple `(f, h, tie_counter, state)`. Khi các trạng thái có cùng giá trị $f$, ưu tiên trạng thái có $h$ nhỏ hơn (tiến gần đích hơn), giúp thuật toán hội tụ thẳng về đích.
- **Chiến lược phân pha Anytime Search trong `solve()`:**
  - **Pha 1 (Optimal Fast Phase):** Chạy A* chuẩn ($w = 1.0$) với $h_{admissible}$ trong ngân sách ngắn ($\min(0.75s, 0.25 \times timebound)$).
    - Giải quyết hoàn hảo Maps 0–8 với số bước **tối ưu 100% khớp BFS**.
  - **Pha 2 (Fast Weighted Phase):** Với các map lớn từ Map 9 trở đi, chuyển ngay sang Weighted A* ($w = 3.0$) kết hợp Heuristic $h_{fast}$ của Hải Anh.
    - Lao cực nhanh về đích, giải quyết trong 0.8s – 3.7s.
  - **Pha 3 (Fallback):** Dự phòng Weighted A* ($w = 2.0$) với $h_{admissible}$ nếu Pha 2 gặp bế tắc.

### 2. Kết quả Benchmark 20 Maps (Timebound = 5s)
- **Tỉ lệ giải thành công: 20/20 MAPS (100% SOLVED)**.
- **Tính hợp lệ:** 100% lời giải đạt `Valid = True`.
- **Tính tối ưu:** Maps 0–8 giữ nguyên số bước tối ưu tuyệt đối (16, 4, 21, 10, 8, 30, 16, 41, 14).
- Toàn bộ Maps 9–19 giải thành công trong thời gian dưới 3.8 giây.


### 3. Bảng số liệu chi tiết 20 maps kiểm chứng (Chạy trên máy Tuấn)

| Map | Trạng thái | Số bước | Expanded | Generated | Unique | Thời gian (s) | Lời giải hợp lệ |
|:---:|:---:|---:|---:|---:|---:|---:|:---:|
| 0 | SOLVED | 16 | 6,299 | 31,957 | 9,226 | 0.19 | True |
| 1 | SOLVED | 4 | 20 | 106 | 57 | 0.00 | True |
| 2 | SOLVED | 21 | 1,231 | 3,342 | 1,511 | 0.03 | True |
| 3 | SOLVED | 10 | 543 | 3,476 | 996 | 0.02 | True |
| 4 | SOLVED | 8 | 231 | 1,522 | 429 | 0.01 | True |
| 5 | SOLVED | 30 | 11,016 | 52,680 | 13,510 | 0.31 | True |
| 6 | SOLVED | 16 | 446 | 2,149 | 768 | 0.01 | True |
| 7 | SOLVED | 41 | 841 | 2,063 | 859 | 0.02 | True |
| 8 | SOLVED | 14 | 3,344 | 30,410 | 11,595 | 0.20 | True |
| 9 | SOLVED | 26 | 6,465 | 69,830 | 29,670 | 0.81 | True |
| 10 | SOLVED | 36 | 12,146 | 103,920 | 43,765 | 0.90 | True |
| 11 | SOLVED | 30 | 16,168 | 142,160 | 51,622 | 0.81 | True |
| 12 | SOLVED | 30 | 16,033 | 138,826 | 47,054 | 0.87 | True |
| 13 | SOLVED | 31 | 21,123 | 137,402 | 46,038 | 0.79 | True |
| 14 | SOLVED | 29 | 18,958 | 122,055 | 40,694 | 0.80 | True |
| 15 | SOLVED | 73 | 13,122 | 126,803 | 53,707 | 1.14 | True |
| 16 | SOLVED | 58 | 15,604 | 153,525 | 52,981 | 1.07 | True |
| 17 | SOLVED | 98 | 36,217 | 335,917 | 102,877 | 3.73 | True |
| 18 | SOLVED | 101 | 36,545 | 337,029 | 122,880 | 3.27 | True |
| 19 | SOLVED | 86 | 16,268 | 150,783 | 56,826 | 1.74 | True |

**Tổng kết:** Đạt tỷ lệ 20/20 maps (100% SOLVED), không có map nào bị TIMEOUT trong ngân sách 5 giây.
## Tuần 3 — Thành viên C(Long): Giảm đối xứng robot

### Baseline trước tối ưu
- Lệnh benchmark: `python benchmark.py --maps 0 5 10 14 --timebound 10`
- Timebound: 10 giây/map
- Benchmark lặp: 3 lần

| Map | Trạng thái / Valid | Steps | Expanded TB | Generated TB | Unique TB | Time TB (s) | Hàm nổi bật trong profile |
|---:|---|---:|---:|---:|---:|---:|---|
| 0 | SOLVED / True | 16 | 6.299 | 31.957 | 9.226 | 0,15 | `successors()` — cumtime 0,135s; `h_admissible()` — 0,080s |
| 5 | SOLVED / True | 30 | 11.016 | 52.680 | 13.510 | 0,22 | `successors()` — cumtime 0,212s; `h_admissible()` — 0,105s |
| 10 | SOLVED / True | 36 | 88.559 | 779.578 | 300.782 | 5,10 | `h_fast()` — cumtime 4,959s; `successors()` — cumtime 3,474s |
| 14 | SOLVED / True | 25 | 23.545 | 151.102 | 55.993 | 0,67 | `successors()` — cumtime 0,389s; `h_admissible()` — 0,299s |

### Phân tích cProfile
- Map 0: `successors()` có cumtime 0,135s; tiếp theo là `h_admissible()` (0,080s).
- Map 5: `successors()` có cumtime 0,212s; tiếp theo là `h_admissible()` (0,105s).
- Map 10: `h_fast()` có cumtime 4,959s; `successors()` 3,474s; các hàm con đáng chú ý là `buoc_di_bo()` (2,441s) và `ket_2x2()` (2,117s).
- Map 14: `successors()` có cumtime 0,389s; tiếp theo là `h_admissible()` (0,299s) và `h_fast()` (0,282s).
- Lệnh profiler: `python profile_solver.py --map <map> --timebound 10`

### Kết quả sau tối ưu
 Benchmark sau tối ưu:
| Map | Status | Steps | Expanded | Generated | Time (s) | Valid |
|---:|---|---:|---:|---:|---:|---|
| 0 | SOLVED | 16 | 4,054 | 20,401 | **0,125** | True |
| 5 | SOLVED | 30 | 7,047 | 33,745 | **0,157** | True |
| 10 | SOLVED | 30 | 73,999.33 | 651,283.33 | **5,057** | True |
| 14 | SOLVED | 25 | 20,198.67 | 129,560 | **0,682** | True |

Kết quả cProfile:
| Map | Bước | Expanded | Generated | Unique | Thời gian profile (s) | Hàm tốn thời gian nổi bật |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 16 | 4.054 | 20.401 | 7.637 | 0,203 | `successors()` 0,090s; `h_admissible()` 0,056s |
| 5 | 30 | 7.047 | 33.745 | 10.820 | 0,309 | `successors()` 0,149s; `h_admissible()` 0,068s |
| 10 | 30 | 69.318 | 611.219 | 245.742 | 9,772 | `h_fast()` 4,250s; `successors()` 3,352s; `h_admissible()` 2,170s; `buoc_di_bo()` 2,128s |
| 14 | 25 | 12.668 | 81.129 | 25.994 | 1,009 | `successors()` 0,371s; `h_admissible()` 0,255s; `h_fast()` 0,246s |

Benchmark đủ 20 map:
| Map | Status | Steps | Expanded | Generated | Unique | Time (s) | Valid |
| --- | ------ | ----: | -------: | --------: | -----: | -------: | ----- |
| 0   | SOLVED |    16 |     4054 |     20401 |   7637 |     0,10 | True  |
| 1   | SOLVED |     4 |       20 |       106 |     57 |     0,00 | True  |
| 2   | SOLVED |    21 |     1231 |      3342 |   1551 |     0,04 | True  |
| 3   | SOLVED |    10 |      358 |      2292 |    933 |     0,01 | True  |
| 4   | SOLVED |     8 |      165 |      1088 |    408 |     0,00 | True  |
| 5   | SOLVED |    30 |     7047 |     33745 |  10820 |     0,15 | True  |
| 6   | SOLVED |    16 |      384 |      1837 |    721 |     0,01 | True  |
| 7   | SOLVED |    41 |      841 |      2063 |    917 |     0,01 | True  |
| 8   | SOLVED |    14 |     3241 |     29526 |  11154 |     0,14 | True  |
| 9   | SOLVED |    24 |    12773 |    138758 |  59025 |     1,25 | True  |
| 10  | SOLVED |    30 |    72695 |    640246 | 255287 |     5,09 | True  |
| 11  | SOLVED |    26 |    11836 |    102780 |  41579 |     0,52 | True  |
| 12  | SOLVED |    24 |    18133 |    154835 |  54567 |     0,86 | True  |
| 13  | SOLVED |    27 |    16341 |    106119 |  39815 |     0,51 | True  |
| 14  | SOLVED |    25 |    20435 |    131122 |  40256 |     0,68 | True  |
| 15  | SOLVED |    73 |   127746 |   1190501 | 526162 |    10,38 | True  |
| 16  | SOLVED |    54 |    90042 |    890783 | 354818 |     6,78 | True  |
| 17  | SOLVED |    98 |   120702 |   1170028 | 521078 |    10,29 | True  |
| 18  | SOLVED |   101 |   112072 |   1099002 | 472556 |    10,28 | True  |
| 19  | SOLVED |    86 |   123009 |   1122116 | 521662 |    10,65 | True  |
### Ghi chú
- Benchmark các map 0, 5, 10 và 14 sử dụng `timebound = 10`, mỗi map chạy 3 lần và lấy kết quả trung bình.
- Số liệu thời gian có thể dao động giữa các lần chạy do ảnh hưởng của môi trường thực thi.
- Số liệu cProfile được lấy từ các lần chạy profiler riêng, không sử dụng thay thế cho thời gian benchmark thông thường.
- Benchmark toàn bộ 20 map sau tối ưu cho kết quả 20/20 SOLVED và tất cả lời giải đều Valid.
- Một số map có kích thước tìm kiếm lớn, đặc biệt Map 15, 17, 18 và 19 có thời gian thực thi khoảng 10 giây hoặc hơn.

### Thay đổi
- Chuẩn hóa vị trí robot trong khóa tìm kiếm bằng `_search_key`, sử dụng tuple robot đã sắp xếp để nhận diện các trạng thái tương đương.
- Không thay đổi thứ tự robot bên trong từng trạng thái gốc, nhằm bảo toàn thông tin action và đường dẫn parent.
- Nhờ đó, các trạng thái chỉ khác nhau về thứ tự robot có thể được xem là cùng một trạng thái khi kiểm tra trùng lặp.
- Không làm thay đổi tính hợp lệ của lời giải hoặc số bước tối ưu tìm được trong các map đã kiểm tra.

### Benchmark trước/sau
- Sau tối ưu, cả bốn map đều giảm số node Expanded và Generated.
- Map 0: Expanded giảm khoảng 35,6%, Generated giảm 36,2%, thời gian từ 0,15s xuống 0,125s.
- Map 5: Expanded giảm khoảng 36,0%, Generated giảm khoảng 35,9%, thời gian từ 0,22s xuống 0,157s.
- Map 10: Expanded và Generated đều giảm khoảng 16,5%. Thời gian gần như không đổi, từ 5,10s xuống 5,057s.
- Map 14: Expanded giảm khoảng 14,2%, Generated giảm khoảng 14,3%. Tuy nhiên, thời gian tăng nhẹ từ 0,67s lên 0,682s.
- Nhìn chung, tối ưu đối xứng robot giúp giảm đáng kể số trạng thái cần xử lý trên cả bốn map. Hiệu quả giảm node rõ rệt hơn mức cải thiện thời gian thực thi.

### Kiểm tra
- Sau thay đổi, cả 4 map benchmark đều SOLVED và lời giải đều Valid.
- Số bước của Map 0, 5 và 14 được giữ nguyên.
- Chạy toàn bộ bộ test 20 map sau tối ưu: SOLVED = 20/20, tất cả lời giải đều Valid.
- Không ghi nhận trường hợp thuật toán trả về lời giải không hợp lệ trong các bộ test đã chạy.
- Kết quả cho thấy việc chuẩn hóa khóa tìm kiếm không làm mất tính đúng đắn của thuật toán và vẫn bảo toàn khả năng tìm lời giải hợp lệ.

### cProfile
- Trước tối ưu, thời gian chủ yếu tập trung ở quá trình sinh trạng thái kế tiếp (`successors()`) và các hàm heuristic như `h_admissible()`, `h_fast()`, cùng các hàm kiểm tra khối 2x2.
- Sau tối ưu, `successors()` và các hàm heuristic vẫn là những thành phần tiêu tốn thời gian chính.
- Map 0: Thời gian cumulative của `successors()` giảm từ 0,135s xuống 0,090s; `h_admissible()` giảm từ 0,080s xuống 0,056s.
- Map 5: `successors()` giảm từ 0,212s xuống 0,149s; `h_admissible()` giảm từ 0,105s xuống 0,068s.
- Map 10: `h_fast()` vẫn là hàm tốn thời gian nổi bật nhất, với 4,250s cumulative; tiếp theo là `successors()` (3,352s), `h_admissible()` (2,170s) và `buoc_di_bo()` (2,128s).
- Map 14: `successors()` có cumulative time 0,371s; tiếp theo là `h_admissible()` (0,255s) và `h_fast()` (0,246s).
- `_search_key()` xuất hiện với số lần gọi lớn, đặc biệt ở Map 10 có 681.305 lần gọi và cumulative time 0,390s. Đây là chi phí bổ sung để chuẩn hóa và nhận diện trạng thái tương đương.
- Tổng thể, kết quả benchmark xác nhận số trạng thái cần xử lý giảm trên cả bốn map. Tuy nhiên, thời gian thực thi không giảm tương ứng trong mọi trường hợp, cho thấy chi phí xử lý bổ sung và các thành phần heuristic vẫn ảnh hưởng đáng kể đến hiệu năng.

### Đếm `unique` theo trạng thái gốc
- `_search_key(state)` vẫn được dùng trong `best_g` để chuẩn hóa thứ tự robot, giúp A* gộp các trạng thái tương đương khi tìm đường.
- Chỉ số `unique` được đếm riêng theo `state.hashable_state()`: tính trạng thái đầu và mỗi trạng thái con ngay khi được sinh, trước khi kiểm tra trùng trong `best_g`.
- Vì vậy, trạng thái con bị loại do `_search_key` đã có vẫn được tính nếu `hashable_state()` của nó là cấu hình mới. Thứ tự robot, `action` và `parent` trong state không bị thay đổi.
- Kiểm tra Map 1: `python benchmark_astar.py --maps 1 --timebound 10`. Kết quả mong đợi sau thay đổi là `SOLVED`, `Valid=True` và `Unique=57`.

## Tuần 3 - Trâm(D): Bộ 5 map tự tạo ; nâng cấp benchmark 

### 1. Bộ custom_maps

| Tên                | Bàn | Tình huống |   Bắt lỗi gì      | Mong đợi    |
|0: vo_nghiem_goc    | 4x3 |Thùng kẹt ở |Solver không trả   |             |
|                    |     |góc trênphải|False,đúng (treo,  | Vô nghiệm   |
|                    |     |góc không   |crash, trả nhầm)   |             |
|                    |     |phải đích   |                   |             |
|1:                  |     |            |                   |             |
|dich_nhieu_hon_thung| 5x3 |2 thùng,    |Heuristic ghép     |             |
|                    |     |3 đích      |cặp sai; solver    | 4 bước      |
|                    |     |            |không hiểu đích    |             |
|                    |     |            |thừa               |             |
|2: thung_da_o_dich  | 5x3 |1 thùng đã  |Heuristic tính     |             |
|                    |     |ở đích nhưng|sai thùng đã ở đích| 5 bước      |
|                    |     |chắn đường  |không biết đi vòng |             |
|                    |     |robot       |                   |             |
|3:mot_robot_re_goc  | 5x4 |1 robot,    |Sai khi đẩy rẽ góc |             |
|                    |     |thùng phải  |đếm sai chi phí đi |8 bước       |
|                    |     |đẩy rẽ góc  |bộ cộng đẩy        |             |
|                    |     |(phải 2,    |                   |             |
|                    |     | xuống 2)   |                   |             |
|4:nhieu_robot       | 5x4 |3 robot, 2  |                   |             |
|                    |     |thùng,2 đích|Lỗi khi nhiều robot|             |
|                    |     |            |(sinh con, validate|8 bước       |
|                    |     |            |khử đối xứng)      |             |

**Cách có đáp án mong đợi:** Tính tay trên giấy trước, rồi đối chiếu với một BFS độc lập (cho nghiệm tối ưu theo định nghĩa). Ví dụ map 3: robot đi tới (1,1) mất 2 bước, đẩy phải 2 lần, robot lên rồi sang (4,0) mất 2 bước, đẩy xuống 2 lần, tổng 8.
**Quy ước Khi sửa custom_maps.py:** Thêm map mới vào cuối danh sách, không đổi tên và toạ độ 5 map cũ, không thêm phần tử thứ tư vào bộ ba. Lý do: test_custom_maps.py, test_heuristic.py và benchmark.py đều lấy map theo tên và "mở gói" bộ ba này; các giá trị mong đợi ở trên tính từ đúng toạ độ hiện tại.

### 2. Kiểm thử 
python -m unittest test_framework
python -m unittest test_custom_maps -v
python -m unittest test_heuristic -v
python autograder.py

**test_custom_maps.py dùng subTest:** một test kiểm tra cả 5 map, map nào sai thì báo đúng tên map cùng giá trị mong đợi và giá trị nhận được. Map vô nghiệm phải trả đúng False (không phải None); các map còn lại phải có lời giải hợp lệ (validate_solution) với gval bằng số bước mong đợi.

**Test bế tắc 2×2:** dùng bốn map phụ, khai báo ngay trong test_heuristic.py. Bàn 6×5, cùng khối 4 ô (2,1), (3,1), (2,2), (3,2)


|Map|	         Mô tả                               | Bế tắc 2×2?       	         | solve mong đợi        |
|A	|4 thùng tạo khối 2×2, chưa thùng nào trên đích| Có	                         |False                  |
|B	|4 thùng tạo khối 2×2, cả 4 nằm trên đích	     | Không (không được loại nhầm)|Trả chính initial_state|
|C	|3 thùng hình chữ L, còn một ô trống trong khối| Không	                     |18 bước (BFS xác nhận) |
|D	|Khối 2×2, 3 thùng đã trên đích, 1 thùng chưa	 | Có                          |False                  |

**Các nhóm test còn lại:** ô chết và khoảng cách đẩy (giá trị tay ở trên); hai heuristic h_admissible và h_fast (h_fast chỉ kiểm tra hữu hạn, không đòi admissible vì Sổ tay ghi nó có thể không admissible); và admissible dọc đường tối ưu trên map 0 đến 8 của thầy (chi phí tối ưu lấy từ BFS độc lập, đồng thời không trạng thái nào trên lời giải bị coi là bế tắc).

### 3. Nâng cấp benchmark
benchmark.py chạy mỗi map trong một tiến trình mới có timeout (tiến trình con chết thì chỉ ghi TIMEOUT hoặc CRASH, bảng vẫn chạy tiếp).

|   Tham số       |	         Công dụng	                                                             |
|--timebound	    |  Thời gian tối đa cho mỗi map (giây), mặc định 30	                               |
|--maps 0 1 2     |	Chỉ chạy các map này (mặc định chạy hết)	                                       |
|--solver <module>|	Chọn module solver (mặc định solution), ví dụ solution_bfs_baseline để so với BFS|
|--set problems   |  Chọn bộ 20 map của thầy hoặc bộ 5 map tự tạo                                    |
|hoặc --set custom|	                                                                                 |
|--md	            |  In thêm bảng Markdown ra màn hình	                                             |
|--out <file>	    |  Ghi bảng Markdown vào file (tự ghi, không cần --md)	                           |

**Các thay đổi khác:** đọc thêm cột Expanded, Generated, Unique từ LAST_STATS của solver (solver không có thống kê thì hiện -); bảng Markdown căn cột thẳng hàng (cột số căn phải), tiêu đề tiếng Anh, thời gian ghi 3 chữ số thập phân cho khớp bảng in ra màn hình.

**Bộ custom:** bảng Markdown có thêm ba cột. Name là tên map, Expected là số bước mong đợi (hoặc "vô nghiệm"), Check là kết quả đối chiếu:


  Check	                      |          Nghĩa là
khớp	                        | Số bước đúng bằng mong đợi
lệch +N / lệch -N	            | Số bước hơn / kém mong đợi N bước
khớp vô nghiệm	              | Map vô nghiệm và solver xác nhận vô nghiệm
không kết luận	              | Hết giờ, chưa biết đúng hay sai
BẤT THƯỜNG:tìm được nghiệm	  | Map đã được xác định vô nghiệm mà solver lại tìm ra nghiệm
KHÔNG KHỚP: không giải được	  | Map có nghiệm mà solver trả False
LỖI: crash / LỖI: lời giải sai|	Crash, hoặc validate_solution báo sai

- Cột này chỉ có ở bảng Markdown; bảng in từng map ra màn hình giữ nguyên, và bộ problems giữ nguyên định dạng cũ. Cột Check dựa vào trường status mà solver ghi trong LAST_STATS; nếu solver ghi nhãn khác quy ước thì đọc thêm cột Status.
- Lệnh chạy thường dùng:
python benchmark.py --timebound 20                                    # 20 map, xem nhanh
python benchmark.py --timebound 120 --md --out results_full.md        # 20 map, bảng cho báo cáo
python benchmark.py --set custom --timebound 20 --md                  # 5 map tự tạo, có cột Check
python benchmark.py --solver solution_bfs_baseline --maps 0 1 2 3 4 5 6 7 --timebound 120   # BFS để đối chiếu

**Chú ý:**Các file results_*.md là file nháp sinh ra từ lệnh trên, không commit (đã ghi trong .gitignore).

## Tuần 4 — Tuấn (A): Nâng cấp Anytime Repairing A* (ARA*) & Gọt tỉa số bước tối ưu

### 1. Động lực và Thiết kế kỹ thuật (Vùng 4 & 5 trong solution.py)
- **Hạn chế Tuần 3:** Weighted A* ở $w=3.0$ giúp giải được 20/20 maps nhưng số bước ở một số map lớn còn dài (ví dụ: Map 9 là 26 bước, Map 11 là 30 bước, Map 12 là 30 bước, Map 14 là 29 bước).
- **Cải tiến Tuần 4 — Giải thuật Anytime Repairing A* (ARA\*):**
  1. **Cắt tỉa cận trên (Cost-Bound Pruning):** Khi đã tìm thấy nghiệm đầu tiên với chi phí $G_{best}$, ta truyền $cost\_bound = G_{best}$ vào vòng lặp tìm kiếm tiếp theo. Bỏ qua mọi trạng thái có $g(s) + h(s) \ge cost\_bound$.
  2. **Tận dụng thời gian còn lại (Refinement Phase):** Sau khi có nghiệm $w=3.0$, thuật toán tận dụng quỹ thời gian còn lại (nếu còn $\ge 1.0$s) để hạ trọng số xuống $w=1.8$ nhằm tìm kiếm đường đi ngắn hơn.

### 2. Kết quả gọt tỉa số bước trên các map lớn (So sánh Tuần 3 vs Tuần 4)

| Map | Số bước Tuần 3 ($w=3.0$) | Số bước Tuần 4 (ARA*) | Mức cải thiện | Thời gian Tuần 4 (s) |
|:---:|:---:|:---:|:---:|:---:|
| **Map 9** | 26 | **24** | **-2 bước (-7.7%)** | 2.27s |
| **Map 11** | 30 | **26** | **-4 bước (-13.3%)** | 0.90s |
| **Map 12** | 30 | **24** | **-6 bước (-20.0%)** | 1.71s |
| **Map 13** | 31 | **27** | **-4 bước (-12.9%)** | 0.88s |
| **Map 14** | 29 | **25** | **-4 bước (-13.8%)** | 1.26s |

- **Kết luận:** Tỷ lệ giải quyết tiếp tục duy trì **20/20 MAPS (100% SOLVED)**, đồng thời tổng số bước trên các map khó giảm đáng kể từ 2 đến 6 bước mỗi map mà vẫn chạy kịp trong ngân sách 5 giây.
