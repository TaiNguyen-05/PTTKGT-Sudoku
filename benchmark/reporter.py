"""
Reporter module for exporting benchmark data to CSV and generating scientific comparison plots.
"""
import csv
from typing import Dict, Any, List
import matplotlib
matplotlib.use('Agg')  # Sử dụng non-interactive backend để vẽ đồ họa không cần mở cửa sổ desktop
import matplotlib.pyplot as plt
import numpy as np
from benchmark.metrics import BenchmarkResults


class BenchmarkReporter:
    @staticmethod
    def export_csv(results: BenchmarkResults, filepath: str = "benchmark_results.csv") -> None:
        """Xuất toàn bộ kết quả đo lường ra file CSV."""
        data = results.to_dict_list()
        if not data:
            return

        keys = data[0].keys()
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def generate_plots(results: BenchmarkResults, output_path: str = "benchmark_comparison.png") -> None:
        """
        Vẽ tổ hợp 3 biểu đồ so sánh khoa học:
        1. Thời gian chạy trung bình theo cấp độ (Logarithmic Scale)
        2. Số lần quay lui (Backtracks)
        3. Tỷ lệ thành công (Success Rate %)
        """
        records = results.records
        if not records:
            return

        # Phân loại theo thuật toán và cấp độ
        algorithms = sorted(list(set(r.algorithm for r in records)))
        difficulties = ["Easy", "Medium", "Hard", "Expert", "Nightmare"]
        present_diffs = [d for d in difficulties if any(r.difficulty.startswith(d) for r in records)]
        if not present_diffs:
            present_diffs = sorted(list(set(r.difficulty for r in records)))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Sudoku Algorithm Performance Comparison (Design & Analysis of Algorithms)", fontsize=14, fontweight="bold")

        bar_width = 0.8 / max(1, len(algorithms))
        x_indices = np.arange(len(present_diffs))

        colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']

        # 1. Biểu đồ Thời gian chạy (Log scale ms)
        for idx, algo in enumerate(algorithms):
            mean_times = []
            for diff in present_diffs:
                times = [r.time_ms for r in records if r.algorithm == algo and r.difficulty.startswith(diff) and r.success]
                mean_times.append(np.mean(times) if times else 0.001)

            offset = (idx - len(algorithms) / 2 + 0.5) * bar_width
            ax1.bar(x_indices + offset, mean_times, bar_width, label=algo, color=colors[idx % len(colors)], alpha=0.85)

        ax1.set_title("Average Execution Time by Difficulty (Log Scale)")
        ax1.set_xlabel("Difficulty Tier")
        ax1.set_ylabel("Execution Time (ms) - Log10")
        ax1.set_yscale('log')
        ax1.set_xticks(x_indices)
        ax1.set_xticklabels(present_diffs)
        ax1.legend(loc="upper left", fontsize=8)
        ax1.grid(True, which="both", ls="--", alpha=0.4)

        # 2. Biểu đồ Số lần quay lui (Mean Backtracks)
        for idx, algo in enumerate(algorithms):
            mean_backtracks = []
            for diff in present_diffs:
                btracks = [r.backtracks for r in records if r.algorithm == algo and r.difficulty.startswith(diff) and r.success]
                mean_backtracks.append(np.mean(btracks) if btracks else 0)

            offset = (idx - len(algorithms) / 2 + 0.5) * bar_width
            ax2.bar(x_indices + offset, mean_backtracks, bar_width, label=algo, color=colors[idx % len(colors)], alpha=0.85)

        ax2.set_title("Average Backtracks Count by Difficulty (Log Scale)")
        ax2.set_xlabel("Difficulty Tier")
        ax2.set_ylabel("Backtracks Count")
        ax2.set_yscale('symlog')
        ax2.set_xticks(x_indices)
        ax2.set_xticklabels(present_diffs)
        ax2.legend(loc="upper left", fontsize=8)
        ax2.grid(True, which="both", ls="--", alpha=0.4)

        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close(fig)
