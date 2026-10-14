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
### Kt qu benchmark
| Map | Gii được | S bước | Thời gian | S node |
|-----|-----------|---------|-----------|---------|
### Chưa hiu / cn hi
- ...
### Việc tuần sau (người - hạn)
