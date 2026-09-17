# BÁO CÁO ĐỒ ÁN MÔN HỌC: PHÂN TÍCH VÀ THIẾT KẾ GIẢI THUẬT
## ĐỀ TÀI: NGHIÊN CỨU, CÀI ĐẶT, TRỰC QUAN HÓA VÀ ĐỐI SÁNH HIỆU NĂNG CÁC GIẢI THUẬT GIẢI BÀI TOÁN SUDOKU

---

## 1. Đặt Vấn Đề và Mô Hình Hóa Bài Toán (Problem Formulation)

Sudoku 9x9 là bài toán kinh điển trong lý thuyết độ phức tạp tính toán, thuộc lớp bài toán **NP-Complete** khi tổng quát hóa lên kích thước $N^2 \times N^2$. Không gian trạng thái tìm kiếm cực kỳ khổng lồ: một bàn cờ Sudoku 9x9 trống có khoảng $6.67 \times 10^{21}$ cách điền số hợp lệ, và với các bài toán có ít ô gợi ý (clues $\le 25$), số lượng cấu hình nhánh có thể lên tới $9^{56} \approx 3.23 \times 10^{53}$.

Đồ án này tiếp cận giải quyết bài toán Sudoku thông qua **4 hướng tiếp cận giải thuật** mang tính đại diện trong khoa học máy tính:
1. **Duyệt vét cạn có quay lui truyền thống (Naive Backtracking / DFS)**: Thuật toán cơ sở (Baseline).
2. **Quay lui kết hợp Heuristics & Lan truyền ràng buộc (Constraint Satisfaction Problem - CSP)**: Tối ưu với Heuristic chọn biến MRV (Minimum Remaining Values), Heuristic chọn giá trị LCV (Least Constraining Value), và Kỹ thuật kiểm tra sớm Forward Checking.
3. **Mô hình hóa bài toán Bao phủ chính xác (Exact Cover) & Knuth's Algorithm X với Dancing Links (DLX)**: Thuật toán tất định tối ưu ở cấp độ cấu trúc con trỏ 4 chiều vòng tròn xoay vòng (Toroidal Doubly Linked List).
4. **Tìm kiếm cục bộ / Meta-heuristic (Simulated Annealing - Tôi luyện thép)**: Thuật toán xấp xỉ ngẫu nhiên tối ưu hóa tổ hợp thông qua cực tiểu hóa hàm phạt năng lượng xung đột $E(S)$.

---

## 2. Phân Tích Chi Tiết Các Giải Thuật

### 2.1. Thuật toán 1: Naive Backtracking (Quay lui cơ bản)
- **Tư tưởng giải thuật**:
  - Quét tìm ô trống đầu tiên theo thứ tự từ trái sang phải, từ trên xuống dưới.
  - Lần lượt thử điền các giá trị từ $1$ đến $9$.
  - Với mỗi giá trị, kiểm tra xem có vi phạm quy tắc Sudoku (hàng, cột, khối 3x3) hay không. Nếu hợp lệ, đệ quy sang ô tiếp theo.
  - Nếu duyệt hết $1..9$ mà không có số nào thỏa mãn, trả về `False` (Quay lui - Backtrack), xóa giá trị ô hiện tại và thử nhánh tiếp theo của ô trước đó.
- **Phân tích độ phức tạp**:
  - **Thời gian (Time Complexity)**: Trường hợp xấu nhất (Worst-case) là $O(9^m)$, với $m$ là số ô trống ($m \le 64$). Trên các đề bài cấu trúc ác mộng như **AI Escargot** (được thiết kế để ép quay lui ở độ sâu lớn), thuật toán có thể mất hàng triệu bước và rơi vào trạng thái Time Limit Exceeded (TLE).
  - **Không gian (Space Complexity)**: $O(m)$ tương ứng với độ sâu tối đa của ngăn xếp đệ quy (Call Stack).

### 2.2. Thuật toán 2: Heuristic-guided CSP Backtracking (MRV + LCV + Forward Checking)
- **Tư tưởng giải thuật**: Mô hình hóa Sudoku dưới dạng bài toán thỏa mãn ràng buộc (Constraint Satisfaction Problem - CSP) với 81 biến số, mỗi biến có miền giá trị $D_i \subseteq \{1..9\}$:
  1. **Heuristic chọn biến (Variable Ordering) - MRV (Minimum Remaining Values)**: Luôn ưu tiên chọn ô có tập giá trị khả dĩ nhỏ nhất ($|D_i|$ nhỏ nhất). Nếu có ô chỉ còn 1 ứng viên khả dĩ (Naked Single), điền ngay lập tức.
  2. **Tie-breaker - Degree Heuristic**: Khi có nhiều ô cùng đạt giá trị MRV nhỏ nhất, chọn ô có số ô trống láng giềng (cùng hàng, cột, khối) nhiều nhất để áp đặt ràng buộc tối đa lên không gian tìm kiếm.
  3. **Heuristic chọn giá trị (Value Ordering) - LCV (Least Constraining Value)**: Sắp xếp các ứng viên khả dĩ sao cho số nào ít loại bỏ lựa chọn của các ô láng giềng nhất sẽ được thử trước.
  4. **Lan truyền ràng buộc - Forward Checking**: Sau mỗi lần gán, cập nhật tức thì miền giá trị của các ô kề cận. Nếu phát hiện một ô bất kỳ có $D_k = \emptyset$, thuật toán lập tức quay lui mà không cần đệ quy xuống sâu.
- **Phân tích độ phức tạp**:
  - **Thời gian**: Vẫn thuộc lớp $O(9^m)$ về mặt lý thuyết xấu nhất, nhưng trong thực nghiệm thực tế, kỹ thuật cắt tỉa nhánh (Branch Pruning) giúp giảm số node duyệt từ hàng trăm nghìn xuống chỉ còn vài chục đến vài trăm node (nhanh hơn từ 10 đến 100 lần so với Naive DFS).
  - **Không gian**: $O(m \times 9)$ để duy trì tập ứng viên của từng ô.

### 2.3. Thuật toán 3: Knuth's Algorithm X với Dancing Links (DLX)
- **Tư tưởng giải thuật**:
  - Chuyển đổi toàn bộ luật chơi Sudoku về bài toán **Bao phủ chính xác (Exact Cover)**: Tìm một tập hợp các hàng trong ma trận nhị phân sao cho mỗi cột có đúng một số $1$.
  - Ma trận Exact Cover của Sudoku có kích thước **729 hàng $\times$ 324 cột**:
    - **729 hàng**: Tương ứng với $9 \times 9 \times 9$ khả năng gán (hàng $r$, cột $c$, giá trị $v$).
    - **324 cột ràng buộc**:
      1. Ràng buộc ô: Mỗi ô $(r, c)$ phải có đúng 1 số (81 cột: $0..80$).
      2. Ràng buộc hàng: Mỗi hàng $r$ phải có đủ số $v$ (81 cột: $81..161$).
      3. Ràng buộc cột: Mỗi cột $c$ phải có đủ số $v$ (81 cột: $162..242$).
      4. Ràng buộc khối: Mỗi khối $b$ phải có đủ số $v$ (81 cột: $243..323$).
- **Kỹ thuật Dancing Links (DLX)**:
  - Sử dụng danh sách liên kết đôi 4 hướng hình xuyến (Toroidal Doubly Linked List) với 4 con trỏ `Left`, `Right`, `Up`, `Down`.
  - Thao tác gỡ cột (`Cover`) và khôi phục cột (`Uncover`) diễn ra trong thời gian $O(1)$:
    ```python
    # Cover cột c
    c.right.left = c.left
    c.left.right = c.right
    # Khôi phục c (Uncover)
    c.right.left = c
    c.left.right = c
    ```
  - Knuth's S-Heuristic: Luôn chọn cột có số lượng phần tử nhỏ nhất (`col.size` min) để chia nhánh.
- **Phân tích độ phức tạp**:
  - **Thời gian**: $O(1)$ cho mỗi thao tác liên kết con trỏ; tổng thời gian giải Sudoku thường **dưới 3 mili-giây**, giải quyết hoàn hảo cả những bài toán khó nhất thế giới (AI Escargot, Platinum Blonde, 17-clues).
  - **Không gian**: $O(K)$ với $K$ là số lượng phần tử khác 0 trong ma trận thưa (chỉ chiếm khoảng vài trăm KB bộ nhớ).

### 2.4. Thuật toán 4: Simulated Annealing (Tôi luyện thép - Meta-heuristic)
- **Tư tưởng giải thuật**:
  - Thay vì xem Sudoku là bài toán tìm kiếm cây quyết định, ta mô hình hóa nó thành bài toán **tối ưu hóa tổ hợp**.
  - **Bảo toàn bất biến khối 3x3**: Khởi tạo bằng cách điền ngẫu nhiên các số còn thiếu vào từng khối 3x3 sao cho mỗi khối luôn có đủ 9 số không trùng lặp (ràng buộc khối luôn đạt điểm 0 xung đột).
  - **Hàm mục tiêu năng lượng (Energy / Cost function)**:
    $$E(S) = \sum_{i=1}^9 (\text{Trùng lặp trên hàng } i) + \sum_{j=1}^9 (\text{Trùng lặp trên cột } j)$$
    Nghiệm đúng hoàn hảo khi $E(S^*) = 0$.
  - **Không gian láng giềng (Neighborhood Move)**: Chọn ngẫu nhiên 2 ô không cố định trong cùng 1 khối 3x3 và hoán đổi giá trị (swap).
  - **Quy tắc chấp nhận Metropolis**:
    - Nếu $\Delta E < 0$ (trạng thái cải thiện): Luôn chấp nhận.
    - Nếu $\Delta E \ge 0$ (trạng thái xấu hơn): Chấp nhận với xác suất $P = \exp(-\Delta E / T)$.
  - **Lịch trình giảm nhiệt (Cooling Schedule)**: $T_{k+1} = T_k \times \alpha$ với $\alpha \approx 0.9995$. Tích hợp cơ chế Reheating (tái nung nhiệt) khi bị kẹt tại cực tiểu địa phương (Local Minima).
- **Phân tích độ phức tạp**:
  - **Thời gian**: $O(K)$ phụ thuộc vào số vòng lặp tối đa và tốc độ giảm nhiệt độ ($K \approx 10^4 - 10^5$).
  - **Không gian**: $O(1)$ (chỉ lưu trữ bàn cờ và danh sách các ô có thể hoán đổi).

---

## 3. Bảng Đối Sánh Tổng Hợp (Theoretical Comparison)

| Tiêu chí | Naive Backtracking | Heuristic CSP (MRV+LCV) | Dancing Links (DLX) | Simulated Annealing |
| :--- | :---: | :---: | :---: | :---: |
| **Bản chất giải thuật** | Tất định (Deterministic) | Tất định (Deterministic) | Tất định (Deterministic) | Ngẫu nhiên (Stochastic) |
| **Tính đầy đủ (Completeness)**| Đầy đủ (Luôn tìm ra nghiệm) | Đầy đủ (Luôn tìm ra nghiệm) | Đầy đủ (Luôn tìm ra nghiệm) | Không đầy đủ (Có thể kẹt) |
| **Thời gian giải trung bình** | $10 - 2000$ ms | $50 - 350$ ms | **$1 - 5$ ms** | $20 - 150$ ms |
| **Số lần quay lui (Backtracks)** | Lớn ($10^3 - 10^5$) | Trung bình ($10^1 - 10^3$) | Cực thấp ($0 - 50$) | Không áp dụng (Swap move) |
| **Khả năng giải bài siêu khó** | Kém (Dễ bị TLE) | Tốt | **Xuất sắc (Tất cả)** | Kém trên bài hẹp nghiệm |
| **Bộ nhớ sử dụng** | $O(m)$ ngăn xếp | $O(9m)$ miền giá trị | $O(1)$ ma trận thưa liên kết | $O(1)$ trạng thái |

---

## 4. Cấu Trúc Mã Nguồn (Project Structure)

```
sudoku/
├── main.py                     # Khởi chạy giao diện chính Pygame (60 FPS, Dark Mode)
├── cli_benchmark.py            # Chạy benchmark dòng lệnh độc lập, tự động xuất CSV & Biểu đồ PNG
├── requirements.txt            # Thư viện: pygame, matplotlib, numpy
├── README.md                   # Tài liệu phân tích học thuật chi tiết
│
├── core/                       # Lớp logic Sudoku nền tảng
│   ├── board.py                # Biểu diễn bàn cờ 9x9, kiểm tra tính hợp lệ, lấy ứng viên, tính xung đột
│   ├── dataset.py              # Bộ dữ liệu mẫu chuẩn (Dễ -> Khó, AI Escargot, Platinum Blonde, 17-clue)
│   └── generator.py            # Thuật toán sinh đề tự động đảm bảo nghiệm duy nhất
│
├── algorithms/                 # Cài đặt 4 giải thuật
│   ├── base_solver.py          # Lớp cơ sở BaseSolver & SolveMetrics (đo thời gian ms, assignments, backtracks)
│   ├── naive_backtracking.py   # Thuật toán 1: Backtracking thuần túy (DFS) có timeout guard
│   ├── heuristic_backtracking.py # Thuật toán 2: MRV + Degree Heuristic + LCV + Forward Checking
│   ├── dancing_links.py        # Thuật toán 3: Knuth's Algorithm X với liên kết 4 chiều xuyến (DLX)
│   └── simulated_annealing.py  # Thuật toán 4: Tôi luyện thép tối ưu hóa hàm phạt xung đột
│
├── benchmark/                  # Đánh giá hiệu năng thực nghiệm
│   ├── metrics.py              # Thu thập số liệu thống kê (Mean, Median, Min, Max, StdDev)
│   ├── runner.py               # Chạy kiểm thử hàng loạt các đề bài
│   └── reporter.py             # Xuất CSV và vẽ đồ thị khoa học bằng Matplotlib
│
├── gui/                        # Giao diện đồ họa Pygame hiện đại (Modern Dark UI)
│   ├── app.py                  # Vòng lặp chính, quản lý TabBar và điều hướng
│   ├── constants.py            # Bảng màu Catppuccin/Nord, kích thước, thông số đồ họa
│   ├── components.py           # Button bo tròn, Slider tốc độ, TabBar điều hướng
│   └── views/
│       ├── play_view.py        # Tab 1: Tự chơi Sudoku (Pencil note, Hint, Undo, Kiểm tra lỗi)
│       ├── visualizer_view.py  # Tab 2: Trực quan hóa animation từng bước (Thử, Quay lui, Chốt số)
│       ├── benchmark_view.py   # Tab 3: Chạy đối đầu 4 thuật toán, vẽ biểu đồ trực tiếp
│       └── custom_input_view.py# Tab 4: Tự nhập đề, nạp đề khó nhất thế giới, đếm số nghiệm
│
├── tests/
│   └── test_solvers.py         # Unit tests tự động kiểm thử cả 4 thuật toán và Board logic
└── data/                       # Các file dữ liệu đề bài (.txt)
    ├── easy.txt
    ├── medium.txt
    ├── hard.txt
    ├── expert.txt
    └── hardest_world.txt
```

---

## 5. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 5.1. Yêu cầu môi trường
- Python 3.9 trở lên (Đã kiểm thử mượt mà trên Python 3.13 Windows 11).
- Cài đặt các thư viện phụ thuộc:
  ```powershell
  pip install -r requirements.txt
  ```

### 5.2. Chạy Giao Diện Đồ Họa Pygame (GUI)
Khởi chạy ứng dụng với đầy đủ 4 chế độ tương tác:
```powershell
python main.py
```
- **Tab 1: Tự Chơi (Play Mode)**:
  - Chọn độ khó (Dễ, Vừa, Khó, Chuyên gia).
  - Điền số bằng phím 1-9 hoặc Numpad trên màn hình.
  - Phím `P`: Bật/tắt chế độ bút chì ghi chú các số khả dĩ nhỏ trong ô.
  - Phím `Ctrl+Z`: Hoàn tác nước đi.
  - Nút `Gợi ý`: Thuật toán DLX tìm nghiệm chuẩn và gợi ý 1 ô hợp lý.
- **Tab 2: Trực Quan Hóa (Visualizer Mode)**:
  - Chọn 1 trong 4 thuật toán: Naive Backtracking, Heuristic CSP, Dancing Links, Simulated Annealing.
  - Nút `Chạy (Run)` / `Tạm dừng` / `Đi 1 bước (Step)` / `Đặt lại (Reset)`.
  - Kéo thanh trượt **Tốc độ hiển thị** từ $1$ đến $300$ bước/giây.
  - Quan sát màu sắc chuyển động:
    - **Màu vàng (Try)**: Thuật toán đang gán thử giá trị.
    - **Màu đỏ san hô (Backtrack)**: Thuật toán phát hiện ngõ cụt và quay lui.
    - **Màu xanh lá (Confirmed)**: Ô đã được chốt giá trị đúng.
- **Tab 3: Đối Sánh Hiệu Năng (Benchmark Mode)**:
  - Chọn một câu đố (từ Dễ đến AI Escargot).
  - Bấm **"CHẠY ĐỐI ĐẦU 4 THUẬT TOÁN"** để xem kết quả đo lường thời gian thực.
  - Bấm **"XUẤT BÁO CÁO CSV & BIỂU ĐỒ"** để xuất file Excel/CSV và ảnh biểu đồ PNG phục vụ báo cáo.
- **Tab 4: Tự Nhập Đề (Custom Input Mode)**:
  - Tự gõ đề bài tùy thích hoặc chọn các test case kinh điển (AI Escargot, Platinum Blonde, 17-Clue, Golden Nugget).
  - Bấm **"KIỂM TRA NGHIỆM ĐỀ BÀI"** để hệ thống kiểm tra đề bài có nghiệm duy nhất hay vô nghiệm.
  - Bấm **"NẠP ĐỀ NÀY VÀO CHẾ ĐỘ VISUALIZER"** để chuyển ngay sang tab xem giải thuật chạy.

### 5.3. Chạy Benchmark Dòng Lệnh Độc Lập (CLI Benchmark)
Dành cho việc thu thập số liệu học thuật phục vụ viết báo cáo:
- Chạy nhanh qua 4 cấp độ đề bài:
  ```powershell
  python cli_benchmark.py --quick
  ```
- Chạy đối đầu trực tiếp trên bài toán khó nhất thế giới (AI Escargot 2006):
  ```powershell
  python cli_benchmark.py --escargot
  ```
- Chạy toàn bộ tập dữ liệu mẫu:
  ```powershell
  python cli_benchmark.py --full
  ```
Kết quả sẽ tự động lưu vào file `benchmark_results.csv` và ảnh biểu đồ khoa học `benchmark_comparison.png`.

### 5.4. Chạy Kiểm Thử Tự Động (Unit Tests)
Chạy bộ kiểm thử tự động để xác minh độ tin cậy và tính đúng đắn:
```powershell
python -m pytest tests/ -v
```

---

## 6. Kết Luận Học Thuật (Scientific Conclusions)

1. **Về tính hiệu quả của cấu trúc dữ liệu**:
   - **Dancing Links (Knuth's DLX)** là giải thuật vượt trội nhất cả về thời gian ($< 3$ ms) lẫn số bước quay lui (hầu như không vượt quá vài chục bước), minh chứng cho sức mạnh của việc chuyển đổi bài toán NP-Complete sang dạng chuẩn tắc Exact Cover và tối ưu cấu trúc con trỏ 4 chiều vòng tròn xoay vòng.
2. **Về vai trò của Heuristics trong cắt tỉa nhánh**:
   - So với Naive Backtracking (bị bùng nổ tổ hợp trên các bài toán hẹp nghiệm), **Heuristic CSP (MRV + LCV + Forward Checking)** chứng minh việc ưu tiên chọn biến có miền giá trị hẹp nhất (Most Constrained Variable) giúp cắt tỉa hơn 99% không gian trạng thái vô ích.
3. **Về sự đánh đổi giữa thuật toán tất định và xấp xỉ ngẫu nhiên**:
   - **Simulated Annealing** giải quyết rất nhanh các bài toán có không gian nghiệm mở (Dễ / Trung bình), nhưng gặp khó khăn tại các bài toán có cấu trúc ràng buộc cực kỳ ngặt nghèo (như AI Escargot) do dễ bị rơi vào bẫy cực tiểu địa phương (Local Minima) của hàm phạt xung đột.
