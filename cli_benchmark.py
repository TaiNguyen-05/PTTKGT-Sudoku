"""
Standalone CLI Benchmark Utility for Sudoku Algorithms.
Usage:
    python cli_benchmark.py --quick
    python cli_benchmark.py --full
    python cli_benchmark.py --escargot
"""
import argparse
import sys
from core.dataset import SAMPLE_PUZZLES, AI_ESCARGOT_REAL
from benchmark.runner import BenchmarkRunner
from benchmark.reporter import BenchmarkReporter


def print_progress(current: int, total: int, pid: str, algo: str):
    percent = (current / total) * 100.0
    sys.stdout.write(f"\r[{percent:5.1f}%] Running {algo:<35} on {pid:<25}")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Sudoku Algorithm Benchmarking CLI")
    parser.add_argument("--quick", action="store_true", help="Chạy kiểm thử nhanh trên 4 câu đố (mỗi cấp độ 1 đề)")
    parser.add_argument("--full", action="store_true", help="Chạy kiểm thử toàn bộ dataset mẫu")
    parser.add_argument("--escargot", action="store_true", help="Chạy đối đầu trực tiếp trên bài toán khó nhất thế giới (AI Escargot)")
    parser.add_argument("--csv", default="benchmark_results.csv", help="Đường dẫn file CSV xuất kết quả")
    parser.add_argument("--plot", default="benchmark_comparison.png", help="Đường dẫn file PNG xuất biểu đồ")

    args = parser.parse_args()

    # Xây dựng danh sách đề bài
    puzzles = []

    if args.escargot:
        puzzles.append({
            "id": "AI_Escargot_2006",
            "difficulty": "Nightmare",
            "puzzle": AI_ESCARGOT_REAL
        })
    elif args.quick or not args.full:
        # Mặc định chạy chế độ quick nếu không chỉ định
        puzzles.append({"id": "Easy_1", "difficulty": "Easy", "puzzle": SAMPLE_PUZZLES["Easy"]["Easy 1 (38 clues)"]})
        puzzles.append({"id": "Medium_1", "difficulty": "Medium", "puzzle": SAMPLE_PUZZLES["Medium"]["Medium 1 (30 clues)"]})
        puzzles.append({"id": "Hard_1", "difficulty": "Hard", "puzzle": SAMPLE_PUZZLES["Hard"]["Hard 1 (26 clues)"]})
        puzzles.append({"id": "Expert_1", "difficulty": "Expert", "puzzle": SAMPLE_PUZZLES["Expert / Nightmare"]["Expert 1 (23 clues)"]})
    else:
        # Full dataset
        for cat, puzzle_dict in SAMPLE_PUZZLES.items():
            for name, puzzle_str in puzzle_dict.items():
                puzzles.append({"id": name, "difficulty": cat, "puzzle": puzzle_str})

    print("=" * 70)
    print("SUDOKU ALGORITHMS EMPIRICAL BENCHMARK (Design & Analysis of Algorithms)")
    print(f"Tổng số đề bài kiểm thử: {len(puzzles)}")
    print("=" * 70)

    runner = BenchmarkRunner()
    results = runner.run_suite(puzzles, progress_callback=print_progress)
    print("\n" + "=" * 70)
    print("BẢNG TỔNG HỢP KẾT QUẢ HIỆU NĂNG (SUMMARY METRICS):")
    print("=" * 70)

    summary = results.get_summary()
    header = f"{'Thuật toán':<40} | {'Mean Time (ms)':<15} | {'Mean Backtracks':<15} | {'Success Rate'}"
    print(header)
    print("-" * len(header))
    for algo, stats in summary.items():
        print(f"{algo:<40} | {stats['Mean Time (ms)']:<15} | {stats['Mean Backtracks']:<15} | {stats['Success Rate (%)']}%")

    # Xuất CSV và biểu đồ
    BenchmarkReporter.export_csv(results, args.csv)
    BenchmarkReporter.generate_plots(results, args.plot)

    print("\n" + "=" * 70)
    print(f"[OK] Đã xuất bảng dữ liệu chi tiết ra: {args.csv}")
    print(f"[OK] Đã xuất biểu đồ đối sánh ra:     {args.plot}")
    print("=" * 70)


if __name__ == "__main__":
    main()
