"""
Benchmark Suite Runner for Sudoku Algorithms.
Executes batch tests across multiple difficulty categories and collects empirical metrics.
"""
from typing import List, Dict, Optional, Callable
import time
from core.board import Board
from algorithms.base_solver import BaseSolver
from algorithms.naive_backtracking import NaiveBacktrackingSolver
from algorithms.heuristic_backtracking import HeuristicBacktrackingSolver
from algorithms.dancing_links import DancingLinksSolver
from algorithms.simulated_annealing import SimulatedAnnealingSolver
from benchmark.metrics import BenchmarkRecord, BenchmarkResults


class BenchmarkRunner:
    def __init__(self, solvers: Optional[List[BaseSolver]] = None):
        if solvers:
            self.solvers = solvers
        else:
            self.solvers = [
                NaiveBacktrackingSolver(),
                HeuristicBacktrackingSolver(),
                DancingLinksSolver(),
                SimulatedAnnealingSolver(max_iterations=15000),
            ]

    def run_suite(
        self,
        puzzles: List[Dict[str, str]],
        progress_callback: Optional[Callable[[int, int, str, str], None]] = None
    ) -> BenchmarkResults:
        """
        Chạy kiểm thử trên danh sách các câu đố.
        Mỗi item trong puzzles là dict: {"id": str, "difficulty": str, "puzzle": str}
        """
        results = BenchmarkResults()
        total_runs = len(puzzles) * len(self.solvers)
        current_run = 0

        for p_idx, p_data in enumerate(puzzles):
            pid = p_data.get("id", f"Puzzle_{p_idx+1}")
            diff = p_data.get("difficulty", "Unknown")
            puzzle_str = p_data["puzzle"]

            for solver in self.solvers:
                current_run += 1
                if progress_callback:
                    progress_callback(current_run, total_runs, pid, solver.name)

                board = Board.from_string(puzzle_str)
                success, metrics = solver.solve(board)

                record = BenchmarkRecord(
                    puzzle_id=pid,
                    difficulty=diff,
                    algorithm=solver.name,
                    time_ms=metrics.execution_time_ms,
                    assignments=metrics.assignments,
                    backtracks=metrics.backtracks,
                    nodes_visited=metrics.nodes_visited,
                    success=success,
                    iterations=metrics.iterations
                )
                results.add_record(record)

        return results
