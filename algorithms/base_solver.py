"""
Base Solver abstraction and metrics collection for Sudoku algorithms.
Provides standard interfaces for both high-speed benchmarking and step-by-step generator visualization.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator, Tuple, Optional
import time
from core.board import Board


@dataclass
class SolveMetrics:
    algorithm_name: str
    execution_time_ms: float
    assignments: int
    backtracks: int
    nodes_visited: int
    success: bool
    iterations: int = 0  # Dùng cho Meta-heuristic (số vòng lặp/thế hệ)

    def to_dict(self):
        return {
            "Algorithm": self.algorithm_name,
            "Time (ms)": round(self.execution_time_ms, 3),
            "Assignments": self.assignments,
            "Backtracks": self.backtracks,
            "Nodes Visited": self.nodes_visited,
            "Success": self.success,
            "Iterations": self.iterations
        }


class BaseSolver(ABC):
    """Lớp cơ sở cho tất cả các giải thuật giải Sudoku."""

    def __init__(self, name: str):
        self.name = name
        self.assignments = 0
        self.backtracks = 0
        self.nodes_visited = 0
        self.iterations = 0

    def reset_metrics(self) -> None:
        self.assignments = 0
        self.backtracks = 0
        self.nodes_visited = 0
        self.iterations = 0

    @abstractmethod
    def solve(self, board: Board) -> Tuple[bool, SolveMetrics]:
        """
        Chạy giải nhanh không sinh generator để benchmark thời gian thực tế chính xác nhất.
        Trả về: (success, SolveMetrics)
        """
        pass

    @abstractmethod
    def solve_stepwise(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        """
        Generator sinh từng bước đi phục vụ Visualizer trên giao diện đồ họa.
        Yield: (row, col, value, action)
        Trong đó action thuộc:
        - 'TRY': Thuật toán đang gán thử giá trị vào ô (row, col)
        - 'BACKTRACK': Thuật toán rút lại giá trị (quay lui)
        - 'CONFIRM': Ô đã được chốt giá trị đúng
        Trả về True nếu giải thành công, False nếu vô nghiệm.
        """
        pass
