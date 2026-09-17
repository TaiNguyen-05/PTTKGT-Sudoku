"""
Meta-heuristic Solver: Simulated Annealing (Tôi luyện thép).
Formulates Sudoku as a combinatorial optimization problem minimizing conflict energy E(S).
Preserves 3x3 box constraint invariant while swapping non-fixed cells within boxes.
Uses the Metropolis acceptance criterion with geometric cooling schedule and reheating.
"""
from typing import Generator, Tuple, List, Dict
import math
import random
import time
from core.board import Board
from algorithms.base_solver import BaseSolver, SolveMetrics


class SimulatedAnnealingSolver(BaseSolver):
    def __init__(self, initial_temp: float = 1.2, cooling_rate: float = 0.9995, max_iterations: int = 100000):
        super().__init__("Simulated Annealing (Meta-heuristic)")
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations

    def _initialize_board(self, board: Board) -> Dict[int, List[Tuple[int, int]]]:
        """
        Khởi tạo bàn cờ:
        - Giữ nguyên các ô cố định ban đầu.
        - Với mỗi khối 3x3, điền các số còn thiếu từ 1..9 ngẫu nhiên vào các ô trống.
        - Đảm bảo ràng buộc khối 3x3 LUÔN LUÔN được thỏa mãn 100%.
        Trả về danh sách các ô có thể hoán đổi trong từng khối 3x3.
        """
        mutable_cells_by_box: Dict[int, List[Tuple[int, int]]] = {b: [] for b in range(9)}

        for b in range(9):
            box_r = (b // 3) * 3
            box_c = (b % 3) * 3

            present = set()
            empty_cells = []

            for r in range(box_r, box_r + 3):
                for c in range(box_c, box_c + 3):
                    val = board.get(r, c)
                    if val != 0:
                        present.add(val)
                    else:
                        empty_cells.append((r, c))
                        mutable_cells_by_box[b].append((r, c))

            missing = list(set(range(1, 10)) - present)
            random.shuffle(missing)

            for idx, (r, c) in enumerate(empty_cells):
                board.set(r, c, missing[idx])

        return mutable_cells_by_box

    def _compute_cost(self, board: Board) -> int:
        """
        Hàm năng lượng E(S) = Tổng số lần trùng lặp trên 9 hàng + Tổng trùng lặp trên 9 cột.
        Vì ràng buộc khối 3x3 đã được bảo toàn 100%, nghiệm hoàn hảo có E(S) = 0.
        """
        return board.count_conflicts()

    def solve(self, board: Board) -> Tuple[bool, SolveMetrics]:
        self.reset_metrics()
        start_time = time.perf_counter()

        mutable_cells = self._initialize_board(board)
        current_cost = self._compute_cost(board)
        best_cost = current_cost
        best_grid = [row[:] for row in board.grid]

        temp = self.initial_temp
        iteration = 0
        stagnation = 0

        # Danh sách các khối có thể hoán đổi (có ít nhất 2 ô trống)
        valid_boxes = [b for b, cells in mutable_cells.items() if len(cells) >= 2]
        if not valid_boxes and current_cost == 0:
            success = True
        else:
            success = False

        while iteration < self.max_iterations and current_cost > 0 and valid_boxes:
            iteration += 1
            self.nodes_visited += 1

            # Chọn ngẫu nhiên 1 khối và 2 ô không cố định trong khối đó
            box = random.choice(valid_boxes)
            cell1, cell2 = random.sample(mutable_cells[box], 2)

            r1, c1 = cell1
            r2, c2 = cell2

            # Hoán đổi thử nghiệm
            v1, v2 = board.get(r1, c1), board.get(r2, c2)
            board.set(r1, c1, v2)
            board.set(r2, c2, v1)
            self.assignments += 2

            new_cost = self._compute_cost(board)
            delta = new_cost - current_cost

            # Tiêu chuẩn chấp nhận Metropolis
            accept = False
            if delta < 0:
                accept = True
            elif temp > 1e-6:
                prob = math.exp(-delta / temp)
                if random.random() < prob:
                    accept = True

            if accept:
                current_cost = new_cost
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_grid = [row[:] for row in board.grid]
                    stagnation = 0
                else:
                    stagnation += 1
            else:
                # Từ chối hoán đổi, hoàn tác
                board.set(r1, c1, v1)
                board.set(r2, c2, v2)
                self.backtracks += 1
                stagnation += 1

            # Hạ nhiệt độ (Cooling schedule)
            temp *= self.cooling_rate

            # Tái nung nhiệt (Reheating) nếu bị kẹt ở cực tiểu địa phương quá lâu
            if stagnation > 8000:
                temp = self.initial_temp * 0.6
                stagnation = 0

            if current_cost == 0:
                success = True
                break

        if not success:
            # Khôi phục trạng thái tốt nhất từng đạt được
            board.grid = [row[:] for row in best_grid]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = SolveMetrics(
            algorithm_name=self.name,
            execution_time_ms=elapsed_ms,
            assignments=self.assignments,
            backtracks=self.backtracks,
            nodes_visited=self.nodes_visited,
            success=success,
            iterations=iteration
        )
        return success, metrics

    def solve_stepwise(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        self.reset_metrics()
        mutable_cells = self._initialize_board(board)
        
        # Báo cáo các ô đã điền ngẫu nhiên ban đầu
        for b, cells in mutable_cells.items():
            for r, c in cells:
                yield (r, c, board.get(r, c), "TRY")

        current_cost = self._compute_cost(board)
        temp = self.initial_temp
        iteration = 0
        stagnation = 0
        valid_boxes = [b for b, cells in mutable_cells.items() if len(cells) >= 2]

        while iteration < 20000 and current_cost > 0 and valid_boxes:
            iteration += 1
            self.nodes_visited += 1

            box = random.choice(valid_boxes)
            cell1, cell2 = random.sample(mutable_cells[box], 2)
            r1, c1 = cell1
            r2, c2 = cell2

            v1, v2 = board.get(r1, c1), board.get(r2, c2)
            board.set(r1, c1, v2)
            board.set(r2, c2, v1)
            self.assignments += 2

            new_cost = self._compute_cost(board)
            delta = new_cost - current_cost

            accept = False
            if delta < 0:
                accept = True
            elif temp > 1e-6:
                prob = math.exp(-delta / temp)
                if random.random() < prob:
                    accept = True

            if accept:
                current_cost = new_cost
                yield (r1, c1, v2, "TRY")
                yield (r2, c2, v1, "TRY")
                stagnation = 0
            else:
                board.set(r1, c1, v1)
                board.set(r2, c2, v2)
                self.backtracks += 1
                stagnation += 1

            temp *= self.cooling_rate
            if stagnation > 5000:
                temp = self.initial_temp * 0.5
                stagnation = 0

            if current_cost == 0:
                for r in range(9):
                    for c in range(9):
                        yield (r, c, board.get(r, c), "CONFIRM")
                return True

        return (current_cost == 0)
