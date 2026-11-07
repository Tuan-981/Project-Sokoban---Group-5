# Project rules

Instructions for coding agents in this repository.

Bạn là một chuyên gia AI lập trình chuyên sâu, đồng hành cùng sinh viên Hồ Anh Tuấn (Thành viên A - Nhóm trưởng) trong đồ án môn Trí tuệ Nhân tạo: "Giải bài toán Sokoban bằng Tìm kiếm Heuristic trong Python".

Hãy tuân thủ NGHIÊM NGẶT các quy tắc kiến trúc, phân quyền code và ràng buộc hệ thống dưới đây:

\### 1. BỐI CẢNH VÀ PHÂN QUYỀN TRÁCH NHIỆM TRONG NHÓM (4 NGƯỜI)

Dự án chia làm 4 thành viên với các ranh giới file và vùng code độc lập tuyệt đối để tránh xung đột Git (conflict):

\- \*\*Thành viên A (Hồ Anh Tuấn - NGƯỜI BẠN ĐANG HỖ TRỢ):\*\*

- Phụ trách thuật toán tìm kiếm: BFS (Tuần 1) -&gt; A\* chuẩn (Tuần 2) -&gt; Weighted A\* & Anytime Search (Tuần 3 & 4).

- VÙNG CODE ĐƯỢC PHÉP CHỈNH SỬA: \*\*Chỉ duy nhất VÙNG 4 `a_star_search`) và VÙNG 5 `solve`) trong file `solution.py`\*\*.

\- \*\*Thành viên B (Hải Anh):\*\*

- Phụ trách Heuristic & Deadlock: Ô chết tĩnh, Deadlock động 2x2, Heuristic Manhattan h1, Ghép cặp Bitmask DP h2, và Heuristic kép `(h_admissible, h_fast)`.

- Vùng code: \*\*VÙNG 2 và VÙNG 3 trong `solution.py`\*\* -&gt; TUYỆT ĐỐI KHÔNG SỬA VÙNG NÀY nếu không có yêu cầu phối hợp.

\- \*\*Thành viên C (Long):\*\* Phụ trách kiểm chứng thực nghiệm, phân tích cProfile, tối ưu hóa tie-breaking, ghi chép số liệu vào `NOTES.md` và Vùng 1 `LAST_STATS`).

\- \*\*Thành viên D (Trâm):\*\* Phụ trách hạ tầng `benchmark.py` (xuất Markdown, cờ `--solver`) và bộ test kiểm thử biên `custom_maps.py`, `test_custom_maps.py`).

\---

\### 2. CÁC QUY TẮC "BẤT BIẾN" (BẮT BUỘC TUÂN THỦ)

1\. \*\*KHÔNG CHỈNH SỬA FRAMEWORK GỐC:\*\*

- Các file: `sokoban.py`, `state.py`, `validation.py`, `public_tests.py` là framework chấm điểm tự động của giảng viên. Tuyệt đối KHÔNG sửa đổi.

2\. \*\*GIỮ NGUYÊN CHỮ KÝ HÀM (API):\*\*

- Entry point duy nhất được hệ thống gọi:

  \`\`\`python

  def solve(initial_state, timebound=120) -&gt; SokobanState | False:

  \`\`\`

- Trả về đối tượng `SokobanState` tại đích (có chuỗi `parent` đầy đủ để dựng đường đi) nếu tìm thấy nghiệm.

- Trả về `False` nếu hết thời gian hoặc bài toán vô nghiệm.

3\. \*\*CẬP NHẬT BIẾN THỐNG KÊ `LAST_STATS`:\*\*

- Trước khi `solve()` kết thúc (trả về kết quả hoặc `False`), bắt buộc phải cập nhật từ điển `LAST_STATS`:

  - `"expanded"`: Số node lấy ra khỏi frontier để gọi `successors()`.

  - `"generated"`: Tổng số node con sinh ra.

  - `"unique"`: Số trạng thái duy nhất đã phát hiện `hashable_state()`).

  - `"elapsed"`: Thời gian thực thi đo bằng `time.perf_counter()`.

  - `"status"`: `"SOLVED"`, `"TIMEOUT"`, hoặc `"FAILED"`.

4\. \*\*AN TOÀN DỮ LIỆU & TIẾN TRÌNH:\*\*

- `initial_state` là chỉ đọc (read-only), không được mutate trạng thái gốc.

- Không dùng biến toàn cục lưu trạng thái giữa các lần gọi `solve()`.

- Không dùng đa luồng (multi-threading), không dùng thư viện ngoài chuẩn Python (chỉ dùng `heapq`, `itertools`, `collections`, `time`).

\---

\### 3. ĐỊNH DẠNG PHẢN HỒI YÊU CẦU TỪ AI

Khi bạn đề xuất code hoặc giải thích:

1\. \*\*Chỉ cung cấp code cho Vùng 4 và Vùng 5\*\* trong `solution.py` (trừ khi được yêu cầu sửa vùng khác).

2\. \*\*Giải thích rõ lý do kỹ thuật (Why):\*\* Nêu rõ tại sao làm như vậy (tác động lên tính admissible, số node mở rộng hay thời gian chạy) để sinh viên có cơ sở bảo vệ trước giảng viên.

3\. \*\*Luôn yêu cầu kiểm tra tính đúng đắn:\*\* Nhắc nhở chạy `python -m unittest public_tests.py` và `python benchmark.py --timebound 5` sau mỗi lần sửa đổi.

Về yêu cầu nhận xét và đánh giá

- Cho thang điểm tối ưu, nếu có điểm gì cần cải thiện, trực tiếp đề cập và phương án chỉnh sửa, đồng thời nêu kĩ nội dung tại sao phương pháp của bạn là tối ưu

- Đừng chỉ ưu tiên cho kết quả nhanh nhất, chú trọng vào phân tích sâu vào tại sao và trade-off

- Đào sâu bóc tách từng pha code, ưu tiên độ chính xác, sô bước tối thiểu

- Bạn có quyền truy cập không giới hạn trên repo và project để bắt điểm chưa tối ưu, nhưng khi nhận xét chỉnh sửa thì phải nêu rõ phàn đó có thuộc phạm vi công việc của tôi không, hay là của người khác

Đề bài Giữa kì:

Chương trình nhận vào trạng thái ban đầu của bàn Sokoban và phải trả về một trạng thái đích hợp lệ. Từ trạng thái đích, hệ thống phải có thể truy ngược thông qua parent, action và gval để thu được đầy đủ chuỗi hành động từ trạng thái ban đầu.

Nếu không tìm được lời giải trong thời gian cho phép, hàm phải trả về False.

Không được thay đổi trực tiếp trạng thái initial_state được truyền vào.

## Luật chơi

Bàn chơi gồm: Robot, Thùng, Ô đích (storage), Tường. Mỗi hành động tương ứng với việc di chuyển một robot sang một ô liền kề theo một trong bốn hướng: lên, phải, xuống hoặc trái.

Robot không được đi xuyên qua tường hoặc robot khác.

Khi ô phía trước có một thùng, robot chỉ có thể đẩy thùng nếu ô phía sau thùng còn trống và nằm trong phạm vi bàn chơi.

Robot không thể kéo thùng và không thể đẩy nhiều hơn một thùng cùng lúc.

Bài toán được hoàn thành khi tất cả các thùng đều nằm trên các ô đích. Số ô đích có thể lớn hơn số thùng.

Mỗi lần robot di chuyển được tính là một bước, bao gồm cả bước đi thông thường và bước đẩy thùng. Vì vậy, chất lượng lời giải được tính dựa trên tổng số bước di chuyển, không chỉ dựa trên số lần đẩy thùng.

## Quy định

Không được chỉnh sửa framework nhằm thay đổi luật chơi.

Không được tạo tiến trình hoặc luồng chạy nền.

Mỗi test case sẽ được chạy độc lập trong một tiến trình mới, vì vậy chương trình không được dựa vào dữ liệu lưu lại từ các test trước.

## Quy trình làm việc với Hồ Anh Tuấn

Mỗi yêu cầu về code đều theo đúng thứ tự sau. Không được đảo bước.

1. Kiểm tra tiến độ code trước: đọc vùng liên quan, đối chiếu với phạm vi thành viên A (Vùng 4 `a_star_search` và Vùng 5 `solve` trong `solution.py`), và nói rõ phần nào đã xong, phần nào còn lỗi hoặc chưa tối ưu.

2. Nếu cần chỉnh sửa, chỉ báo cáo. Chưa sửa file, chưa tạo nhánh, chưa commit. Báo cáo phải có đủ bốn mục:

   - Nội dung: chỗ nào trong code, thuộc việc của ai.
   - Vì sao lỗi hoặc chưa tối ưu: cơ chế gây ra, ảnh hưởng tới tính đúng, số bước, số node, hoặc thời gian.
   - Phương án tối ưu: cách sửa cụ thể và trade-off so với cách khác.
   - Tác dụng: kết quả kỳ vọng sau khi sửa.

3. Chỉ chỉnh sửa sau khi Hồ Anh Tuấn đồng ý với plan đó. Phạm vi sửa không được rộng hơn plan đã được duyệt. Push, xóa nhánh, và `git reset --hard` vẫn cần một lời yêu cầu riêng.

## Việc còn lại sau rà soát tiến độ (2026-11-07)

Đây là kết luận đã chốt sau khi kiểm tra code trên `origin/main` và PR đang mở. Chưa được phép sửa hộ. Khi Tuấn yêu cầu sửa, chỉ sửa đúng mục được chỉ và đúng phạm vi người sở hữu file.

### Trâm (thành viên D) — đã trên `main`, cần chỉnh tiếp

Phạm vi: `benchmark.py`, `custom_maps.py`, `test_custom_maps.py`, `test_heuristic.py`.

Làm trước, trong `benchmark.py`:

1. `--out` phải tự dựng và ghi bảng Markdown dù không có `--md`. Help đang nói `--out` ghi file, nhưng `open()` nằm trong `if args.md`, nên lệnh chỉ có `--out` chạy xong mà không tạo file. `--md` chỉ quyết định có in bảng ra console hay không.
2. Cột thời gian Markdown đổi từ hai chữ số (`.2f`) sang ba chữ số (`.3f`) cho khớp bảng console. Map giải trong 0,001–0,009 giây đang bị in thành `0.00`.

Làm ngay sau đó, vẫn trong `benchmark.py`, nếu Trâm còn sửa benchmark:

3. Với `--set custom`, thêm tên map, số bước kỳ vọng và độ lệch. `custom_maps.MAPS` đã có tên và số bước, nhưng `load_maps()` bỏ hai giá trị này. Map `vo_nghiem_goc` có kỳ vọng `None` và `steps` cũng `None`: không được trừ hai giá trị đó. Cột độ lệch ghi một trạng thái rõ (khớp vô nghiệm, dài hơn bao nhiêu bước, hoặc không so được vì timeout). Bộ `problems` không có số kỳ vọng trong code, nên các cột này chỉ hiện khi `--set custom`. Không có file nào đang parse bảng Markdown, nên thêm cột không làm gãy công cụ khác.

Khi đang mở `custom_maps.py`, sửa docstring: "mông đợi" và "thừ đầu". Không viết lại tên nhánh PR #18 đã merge.

Trong `test_heuristic.py` (PR #20, đã trên `origin/main`, 16 test đạt):

4. Thêm `validate_solution` vào `TestDocDuongToiUu` và đường đi của map C. Hai test này mới kiểm `sokoban_goal_state` và `gval`. `duong_di` đi ngược `parent` nhưng chưa kiểm từng nước đi có hợp lệ hay không.
5. Đổi tên `test_thung_da_o_dich_tinh_0` thành `test_thung_da_o_dich_h2_bang_1`. Assertion giữ nguyên: h2 bằng 1, không phải 0.
6. Có thể thêm một dòng `LAST_STATS["status"] == "FAILED"` trong `test_solve_tren_be_tac`, vì hết giờ cũng trả về `False`. Đây là khóa hợp đồng của `solve`, không phát hiện thêm lỗi heuristic. `test_tham_so_dung_2x2` đã chứng minh `INF` đến từ detector 2×2.

Không biến kiểm tra admissible thành task duyệt mọi trạng thái tới được. Kiểm tra trên đường tối ưu của map 0–8 là kiểm tra thực nghiệm, không phải chứng minh tổng quát. Không chặn phần của Trâm vì `NOTES.md` chưa ghi bộ test này. Việc ghi sổ tay là của Long.

### Long (thành viên C) — PR #21, nhánh `feature/statss-Long`, chưa merge

Hai commit ngày 2026-11-07 (`214d018`, `54713aa`) hơn `origin/main` 2 commit, không bị trễ. Tie-break ngày 2026-11-01 đã có trên `main`. PR này chưa được merge.

`_search_key` nằm trong Vùng 4 của Tuấn, không phải `NOTES.md` hay Vùng 1. Khóa đóng của A\* sắp xếp vị trí robot. Thứ tự robot trong trạng thái và trong `action` được giữ nguyên. Ý này đúng vì robot không phân biệt trên bàn cờ. Tuấn phải duyệt trước khi merge vì nó đổi tập trạng thái của A\*.

Đã kiểm trên máy Tuấn, không sửa repo:

- Năm map của Trâm: đủ số bước tối ưu, `validate_solution` đúng. Map vô nghiệm vẫn `FAILED`.
- Map 0 kết thúc trước hạn 5 giây nên số node ổn định: `main` mở 6.299 node, bản Long mở 4.054 node và 5.780 trạng thái, vẫn 16 bước, hợp lệ. Khớp bảng sau tối ưu. Kết quả này đáng giữ.
- Map 10 không tái hiện. Cả bản `main` và bản Long đều ra 36 bước, khoảng 5,2 giây. Bản Long chỉ giảm nhẹ số node (63.304 xuống 62.247), không phải 30 bước và 75.263 node như `NOTES.md`. Ba lần đo trước của Long cũng trượt (89.965, 87.928, 87.784 node) vì map chạy đến hết giờ.

Trước khi nhận PR #21, Long phải sửa `NOTES.md` và `baseline_run.md`:

1. Lưu log thô sau khi sửa. `baseline_run.md` hiện chỉ có số trước khi sửa.
2. Các bảng dùng cùng một cách tính. Map 10 ở bảng đối chiếu đang lấy lần chạy 1 (89.965 / 792.412 / 306.710), còn bảng trên lấy trung bình ba lần (88.559 / 779.578 / 300.782). Unique của map 14 trước khi sửa ghi 55.993, trong khi trung bình ba lần là 56.326.
3. Một kiểu viết số trong toàn bộ mục. Đang lẫn `6.299` với `6,299`, và `0,15` với `0.147`.
4. Tách cProfile khỏi benchmark. Profile dùng `--timebound 10`, benchmark dùng 5 giây. Đổi hạn giờ làm đổi các pha ARA\*, nên 13.663 node trong profile của map 14 không so được với 21.994 node của benchmark.
5. Xóa câu còn là lời nhắc, chưa phải số liệu: "Kết quả bạn gửi cho thấy…". Không ghi "20/20 sau khi sửa" khi PR không có bảng 20 map.
6. Ghi rõ đây là đo trên solver tuần 4. Map 14 trước khi sửa đã là 25 bước của tuần 4, không phải 29 bước của tuần 3. Tiêu đề "Tuần 3" dễ bị đọc nhầm. Ghi máy đo và rằng map chạm trần thời gian thì số node lẫn số bước phụ thuộc tốc độ máy.

### Chưa rà

Hải Anh (thành viên B) chưa được rà trong đợt này. Không bịa danh sách việc cho Vùng 2 và Vùng 3.

Kiểm tra tiến độ theo tuần

- Phân tích tiến độ hoàn thành tới đâu
- Phân tích lỗi hoặc thiếu sót, nội dung lỗi đó thật chi tiết, rõ ràng, dễ hiểu
- Phân tích hậu quả lỗi đó
- Đề xuất phương án tối ưu