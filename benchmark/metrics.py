"""
Metrics tracking and aggregation for benchmarking Sudoku algorithms.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
import statistics


@dataclass
class BenchmarkRecord:
    puzzle_id: str
    difficulty: str
    algorithm: str
    time_ms: float
    assignments: int
    backtracks: int
    nodes_visited: int
    success: bool
    iterations: int = 0


class BenchmarkResults:
    def __init__(self):
        self.records: List[BenchmarkRecord] = []

    def add_record(self, record: BenchmarkRecord):
        self.records.append(record)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [
            {
                "Puzzle ID": r.puzzle_id,
                "Difficulty": r.difficulty,
                "Algorithm": r.algorithm,
                "Time (ms)": round(r.time_ms, 3),
                "Assignments": r.assignments,
                "Backtracks": r.backtracks,
                "Nodes Visited": r.nodes_visited,
                "Success": r.success,
                "Iterations": r.iterations,
            }
            for r in self.records
        ]

    def get_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Tính toán Mean, Median, Min, Max, StdDev theo từng thuật toán.
        """
        by_algo: Dict[str, List[BenchmarkRecord]] = {}
        for r in self.records:
            by_algo.setdefault(r.algorithm, []).append(r)

        summary = {}
        for algo, recs in by_algo.items():
            times = [r.time_ms for r in recs if r.success]
            backtracks = [r.backtracks for r in recs if r.success]
            success_count = sum(1 for r in recs if r.success)
            total = len(recs)

            summary[algo] = {
                "Total Puzzles": total,
                "Success Count": success_count,
                "Success Rate (%)": round((success_count / total) * 100, 1) if total > 0 else 0,
                "Mean Time (ms)": round(statistics.mean(times), 3) if times else 0.0,
                "Median Time (ms)": round(statistics.median(times), 3) if times else 0.0,
                "Min Time (ms)": round(min(times), 3) if times else 0.0,
                "Max Time (ms)": round(max(times), 3) if times else 0.0,
                "Mean Backtracks": round(statistics.mean(backtracks), 1) if backtracks else 0,
                "Max Backtracks": max(backtracks) if backtracks else 0,
            }

        return summary
