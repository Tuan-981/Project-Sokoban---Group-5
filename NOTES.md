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

### Chưa hiu / cn hi
- ...
### Việc tuần sau (người - hạn)
