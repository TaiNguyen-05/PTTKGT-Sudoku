"""
Naive Backtracking Solver (Baseline Brute-force Depth-First Search).
Scans row-by-row, col-by-col and tests digits 1 to 9 sequentially.
Complexity: Time O(9^m), Space O(m) where m is the count of empty cells.
"""
from typing import Generator, Tuple
import time
from core.board import Board
from algorithms.base_solver import BaseSolver, SolveMetrics


class NaiveBacktrackingSolver(BaseSolver):
    def __init__(self, max_nodes: int = 250000, timeout_sec: float = 3.0):
        super().__init__("Naive Backtracking (DFS)")
        self.max_nodes = max_nodes
        self.timeout_sec = timeout_sec
        self.timed_out = False
        self._start_time = 0.0

    def solve(self, board: Board) -> Tuple[bool, SolveMetrics]:
        self.reset_metrics()
        self.timed_out = False
        self._start_time = time.perf_counter()
        
        success = self._solve_fast(board)
        
        elapsed_ms = (time.perf_counter() - self._start_time) * 1000.0
        metrics = SolveMetrics(
            algorithm_name=self.name,
            execution_time_ms=elapsed_ms,
            assignments=self.assignments,
            backtracks=self.backtracks,
            nodes_visited=self.nodes_visited,
            success=success
        )
        return success, metrics

    def _solve_fast(self, board: Board) -> bool:
        self.nodes_visited += 1
        if self.nodes_visited > self.max_nodes:
            self.timed_out = True
            return False

        if (self.nodes_visited % 5000 == 0) and (time.perf_counter() - self._start_time > self.timeout_sec):
            self.timed_out = True
            return False

        empty = board.find_empty_cell()
        if empty is None:
            return True  

        r, c = empty
        for val in range(1, 10):
            if board.is_valid_placement(r, c, val):
                board.set(r, c, val)
                self.assignments += 1
                
                if self._solve_fast(board):
                    return True
                
                # Quay lui
                board.clear(r, c)
                self.backtracks += 1

                if self.timed_out:
                    return False

        return False

    def solve_stepwise(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        """
        Phiên bản generator sinh từng bước thực thi cho Visualizer UI.
        """
        self.reset_metrics()
        success = yield from self._solve_generator(board)
        return success

    def _solve_generator(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        self.nodes_visited += 1
        empty = board.find_empty_cell()
        if empty is None:
            return True

        r, c = empty
        for val in range(1, 10):
            if board.is_valid_placement(r, c, val):
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
