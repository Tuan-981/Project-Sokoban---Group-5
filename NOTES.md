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
## Tuần 1 — Thành viên H Anh : Heuristic tổng khoảng cách đẩy

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


# Thống nhất cách đếm node mở rộng; chuẩn bị mẫu bảng số liệu 

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
## Long —Thống kê BFS và kiểm thử PROBLEMS (16/10/2026)

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
- Lệnh chạy: python benchmark.py --timebound 5 (Lệnh này chạy các map từ 0 đến 19, mỗi map có ngân sách 5 giây.)
Chạy trong cùng môi trường Python, `timebound=0.1` giây/map. Đây là lần chạy thử nhanh để kiểm tra thống kê, **không phải kết luận hiệu năng cuối cùng**. Các map `TIMEOUT` chưa tìm được lời giải trong ngân sách này.

Map  Status     Steps   Expanded  Generated   Unique   Time(s)  Valid
------------------------------------------------------------------------------
0    SOLVED        16      38626     188680    51917     0.580  True
1    SOLVED         4         56        319      127     0.001  True
2    SOLVED        21       4136      10887     4629     0.031  True
3    SOLVED        10       6458      40280    10875     0.300  True
4    SOLVED         8        928       5877     1498     0.015  True
5    SOLVED        30     128745     604658   142407     2.056  True
6    SOLVED        16       5593      27433     7319     0.073  True
7    SOLVED        41       2308       5652     2346     0.015  True
8    RUNNING     None     179236    1640795   413694     5.282  -
9    RUNNING     None     132499    1506895   389413     5.439  -
10 
**Lưu ý về timeout:** kiểm tra deadline được thực hiện giữa các lần mở rộng. Một lần gọi `successors()` có thể tốn nhiều thời gian, nên thời gian thực tế đôi khi vượt `timebound` (đặc biệt map 5). Đây là điểm cần ghi nhận khi tối ưu tiếp; không được hiểu timeout 0.1 giây là giới hạn cứng tuyệt đối.

### Nhận xét
- 7/20 map được giải trong lần chạy nhanh này; cả 7 lời giải đều qua validator.
- BFS vẫn phù hợp làm baseline đúng đắn nhưng tăng số trạng thái nhanh trên các map khó; cần benchmark lại với ngân sách dài hơn và so sánh A* trên cùng map.
- `StateSpace.n` không được dùng thay cho `expanded`: nó đếm số đối tượng trạng thái được khởi tạo.


### Chưa hiu / cn hi
- ...
### Việc tuần sau (người - hạn)
