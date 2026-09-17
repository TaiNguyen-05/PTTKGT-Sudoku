"""
Heuristic-guided Backtracking Solver (CSP with MRV, Degree Heuristic, Forward Checking, LCV).
Selects variables by Minimum Remaining Values (MRV) + Degree Heuristic tie-breaker,
and orders values by Least Constraining Value (LCV).
Significantly reduces state-space search nodes compared to naive DFS.
"""
from typing import Generator, Tuple, List, Set, Optional
import time
from core.board import Board
from algorithms.base_solver import BaseSolver, SolveMetrics


class HeuristicBacktrackingSolver(BaseSolver):
    def __init__(self):
        super().__init__("Heuristic CSP (MRV + LCV + Forward Checking)")

    def solve(self, board: Board) -> Tuple[bool, SolveMetrics]:
        self.reset_metrics()
        start_time = time.perf_counter()

        success = self._solve_fast(board)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = SolveMetrics(
            algorithm_name=self.name,
            execution_time_ms=elapsed_ms,
            assignments=self.assignments,
            backtracks=self.backtracks,
            nodes_visited=self.nodes_visited,
            success=success
        )
        return success, metrics

    def _select_mrv_variable(self, board: Board) -> Tuple[Optional[Tuple[int, int]], Set[int]]:
        """
        Chọn biến theo MRV (Minimum Remaining Values).
        Nếu hòa (tie), dùng Degree Heuristic (ô có nhiều ô trống láng giềng nhất).
        """
        min_cands_count = 10
        best_cell = None
        best_cands = set()
        max_degree = -1

        for r in range(9):
            for c in range(9):
                if board.get(r, c) == 0:
                    cands = board.get_candidates(r, c)
                    cand_count = len(cands)
                    
                    # Nếu có ô không còn ứng viên nào hợp lệ -> Ngõ cụt ngay lập tức!
                    if cand_count == 0:
                        return (r, c), set()

                    if cand_count < min_cands_count:
                        min_cands_count = cand_count
                        best_cell = (r, c)
                        best_cands = cands
                        max_degree = self._get_degree(board, r, c)
                        # Nếu chỉ còn 1 ứng viên duy nhất (Naked Single), ưu tiên điền ngay
                        if min_cands_count == 1:
                            return best_cell, best_cands
                    elif cand_count == min_cands_count:
                        # Tie-breaker bằng Degree Heuristic
                        deg = self._get_degree(board, r, c)
                        if deg > max_degree:
                            max_degree = deg
                            best_cell = (r, c)
                            best_cands = cands

        return best_cell, best_cands

    def _get_degree(self, board: Board, row: int, col: int) -> int:
        """Đếm số ô trống láng giềng (cùng hàng, cột, khối 3x3)."""
        count = 0
        box_r = (row // 3) * 3
        box_c = (col // 3) * 3

        for i in range(9):
            if i != col and board.get(row, i) == 0:
                count += 1
            if i != row and board.get(i, col) == 0:
                count += 1

        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if (r != row or c != col) and board.get(r, c) == 0:
                    # Tránh đếm lặp các ô đã tính ở hàng/cột
                    if r != row and c != col:
                        count += 1

        return count

    def _order_values_lcv(self, board: Board, row: int, col: int, candidates: Set[int]) -> List[int]:
        """
        Sắp xếp các giá trị theo Least Constraining Value (LCV).
        Giá trị nào ít loại bỏ lựa chọn của các ô láng giềng nhất sẽ được thử trước.
        """
        if len(candidates) <= 1:
            return list(candidates)

        # Đếm số lượng ứng viên bị loại bỏ trên các ô trống láng giềng
        def count_eliminations(val: int) -> int:
            eliminated = 0
            box_r = (row // 3) * 3
            box_c = (col // 3) * 3

            # Kiểm tra hàng & cột
            for i in range(9):
                if i != col and board.get(row, i) == 0:
                    if val in board.get_candidates(row, i):
                        eliminated += 1
                if i != row and board.get(i, col) == 0:
                    if val in board.get_candidates(i, col):
                        eliminated += 1

            # Kiểm tra khối
            for r in range(box_r, box_r + 3):
                for c in range(box_c, box_c + 3):
                    if r != row and c != col and board.get(r, c) == 0:
                        if val in board.get_candidates(r, c):
                            eliminated += 1

            return eliminated

        return sorted(list(candidates), key=count_eliminations)

    def _solve_fast(self, board: Board) -> bool:
        self.nodes_visited += 1

        cell, candidates = self._select_mrv_variable(board)
        if cell is None:
            return True  # Không còn ô trống nào -> Thành công

        if len(candidates) == 0:
            return False  # Forward Checking phát hiện miền giá trị rỗng -> Cắt nhánh!

        r, c = cell
        ordered_vals = self._order_values_lcv(board, r, c, candidates)

        for val in ordered_vals:
            board.set(r, c, val)
            self.assignments += 1

            if self._solve_fast(board):
                return True

            board.clear(r, c)
            self.backtracks += 1

        return False

    def solve_stepwise(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        self.reset_metrics()
        success = yield from self._solve_generator(board)
        return success

    def _solve_generator(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        self.nodes_visited += 1

        cell, candidates = self._select_mrv_variable(board)
        if cell is None:
            return True

        if len(candidates) == 0:
            return False

        r, c = cell
        ordered_vals = self._order_values_lcv(board, r, c, candidates)

        for val in ordered_vals:
            board.set(r, c, val)
            self.assignments += 1
            yield (r, c, val, "TRY")

            result = yield from self._solve_generator(board)
            if result:
                yield (r, c, val, "CONFIRM")
                return True

            board.clear(r, c)
            self.backtracks += 1
            yield (r, c, 0, "BACKTRACK")

        return False
