"""
Head-to-Head Algorithm Comparison & Benchmark View.
Runs all 4 algorithms on the same puzzle and displays a live comparative table and visual bar charts.
Provides buttons to export CSV and PNG plots.
"""
import pygame
import time
from typing import List, Dict, Any, Optional
from core.board import Board
from core.dataset import SAMPLE_PUZZLES, AI_ESCARGOT_REAL
from algorithms.naive_backtracking import NaiveBacktrackingSolver
from algorithms.heuristic_backtracking import HeuristicBacktrackingSolver
from algorithms.dancing_links import DancingLinksSolver
from algorithms.simulated_annealing import SimulatedAnnealingSolver
from benchmark.metrics import BenchmarkRecord, BenchmarkResults
from benchmark.reporter import BenchmarkReporter
from gui.constants import (
    BOARD_X, BOARD_Y, BOARD_SIZE, COLOR_SURFACE, COLOR_SURFACE_LIGHT,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_TEXT_ACCENT,
    COLOR_BTN_PRIMARY, COLOR_BTN_SECONDARY, COLOR_BTN_SUCCESS, COLOR_BTN_DANGER
)
from gui.components import Button


class BenchmarkView:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.current_puzzle_name = "Medium 1 (30 clues)"
        self.current_puzzle_str = SAMPLE_PUZZLES["Medium"]["Medium 1 (30 clues)"]
        self.results: List[Dict[str, Any]] = []
        self.is_running = False
        self.status_msg = "Chọn đề bài và bấm 'Chạy đối đầu' để đo đạc số liệu."

        # Solvers
        self.solvers = [
            DancingLinksSolver(),
            HeuristicBacktrackingSolver(),
            NaiveBacktrackingSolver(max_nodes=100000, timeout_sec=2.0),
            SimulatedAnnealingSolver(max_iterations=10000),
        ]

        # Buttons
        self.btn_easy = Button(50, 110, 110, 36, "Đề Dễ", lambda: self._set_puzzle("Easy", "Easy 1 (38 clues)"), font_size=14)
        self.btn_med = Button(170, 110, 110, 36, "Đề Vừa", lambda: self._set_puzzle("Medium", "Medium 1 (30 clues)"), font_size=14)
        self.btn_hard = Button(290, 110, 110, 36, "Đề Khó", lambda: self._set_puzzle("Hard", "Hard 1 (26 clues)"), font_size=14)
        self.btn_expert = Button(410, 110, 110, 36, "Chuyên gia", lambda: self._set_puzzle("Expert / Nightmare", "Expert 1 (23 clues)"), font_size=14)
        self.btn_escargot = Button(530, 110, 150, 36, "AI Escargot", self._set_escargot, font_size=14, bg_color=COLOR_BTN_DANGER, text_color=(20, 20, 30))

        self.btn_run = Button(710, 105, 260, 46, "CHẠY ĐỐI ĐẦU 4 THUẬT TOÁN", self._run_benchmark, bg_color=COLOR_BTN_SUCCESS, text_color=(20, 20, 30), font_size=15)
        self.btn_export = Button(990, 105, 240, 46, "XUẤT BÁO CÁO CSV & BIỂU ĐỒ", self._export_report, bg_color=COLOR_BTN_PRIMARY, text_color=(20, 20, 30), font_size=14)

    def _set_puzzle(self, cat: str, name: str):
        self.current_puzzle_name = name
        self.current_puzzle_str = SAMPLE_PUZZLES[cat][name]
        self.status_msg = f"Đã chọn: {name}. Sẵn sàng chạy đối đầu."

    def _set_escargot(self):
        self.current_puzzle_name = "AI Escargot (World's Hardest 2006)"
        self.current_puzzle_str = AI_ESCARGOT_REAL
        self.status_msg = "Đã chọn AI Escargot. Thử thách độ phức tạp cực đại!"

    def _run_benchmark(self):
        self.is_running = True
        self.results = []
        self.status_msg = "Đang chạy đo đạc thời gian thực..."

        for solver in self.solvers:
            board = Board.from_string(self.current_puzzle_str)
            success, metrics = solver.solve(board)
            self.results.append(metrics.to_dict())

        self.is_running = False
        self.status_msg = f"Đã hoàn thành đo đạc 4 thuật toán trên '{self.current_puzzle_name}'!"

    def _export_report(self):
        if not self.results:
            self.status_msg = "Vui lòng chạy benchmark trước khi xuất báo cáo!"
            return

        bench_results = BenchmarkResults()
        for r in self.results:
            bench_results.add_record(BenchmarkRecord(
                puzzle_id=self.current_puzzle_name,
                difficulty="Current",
                algorithm=r["Algorithm"],
                time_ms=r["Time (ms)"],
                assignments=r["Assignments"],
                backtracks=r["Backtracks"],
                nodes_visited=r["Nodes Visited"],
                success=r["Success"],
                iterations=r.get("Iterations", 0)
            ))

        BenchmarkReporter.export_csv(bench_results, "benchmark_results.csv")
        BenchmarkReporter.generate_plots(bench_results, "benchmark_comparison.png")
        self.status_msg = "Đã xuất file 'benchmark_results.csv' và biểu đồ 'benchmark_comparison.png'!"

    def handle_event(self, event: pygame.event.Event) -> None:
        self.btn_easy.handle_event(event)
        self.btn_med.handle_event(event)
        self.btn_hard.handle_event(event)
        self.btn_expert.handle_event(event)
        self.btn_escargot.handle_event(event)
        self.btn_run.handle_event(event)
        self.btn_export.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        font_title = self.fonts["title"]
        font_ui = self.fonts["ui"]
        font_small = self.fonts["small"]

        # Tiêu đề
        title_surf = font_title.render("ĐỐI SÁNH HIỆU NĂNG THỰC NGHIỆM (HEAD-TO-HEAD BENCHMARK)", True, COLOR_TEXT_ACCENT)
        surface.blit(title_surf, (50, 70))

        # Vẽ các nút
        self.btn_easy.draw(surface, font_small)
        self.btn_med.draw(surface, font_small)
        self.btn_hard.draw(surface, font_small)
        self.btn_expert.draw(surface, font_small)
        self.btn_escargot.draw(surface, font_small)
        self.btn_run.draw(surface, font_ui)
        self.btn_export.draw(surface, font_ui)

        # 1. Bảng số liệu chi tiết (Table)
        table_rect = pygame.Rect(50, 175, 1180, 240)
        pygame.draw.rect(surface, COLOR_SURFACE, table_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, table_rect, width=1, border_radius=8)

        # Header Bảng
        headers = ["Thuật toán (Algorithm)", "Thời gian (Time ms)", "Số lần gán (Assignments)", "Số lần quay lui (Backtracks)", "Đỉnh duyệt (Nodes Visited)", "Kết quả (Status)"]
        col_x = [70, 410, 570, 750, 930, 1100]

        pygame.draw.rect(surface, COLOR_SURFACE_LIGHT, (50, 175, 1180, 42), border_top_left_radius=8, border_top_right_radius=8)
        for i, h in enumerate(headers):
            surface.blit(font_small.render(h, True, COLOR_TEXT_ACCENT), (col_x[i], 188))

        # Rows
        if self.results:
            for idx, res in enumerate(self.results):
                row_y = 230 + idx * 42
                # Đường phân cách hàng
                pygame.draw.line(surface, COLOR_SURFACE_LIGHT, (60, row_y + 35), (1220, row_y + 35), 1)

                algo_name = res["Algorithm"]
                time_str = f"{res['Time (ms)']:.3f} ms"
                assign_str = f"{res['Assignments']:,}"
                backtrack_str = f"{res['Backtracks']:,}"
                nodes_str = f"{res['Nodes Visited']:,}"
                status_str = "THÀNH CÔNG" if res["Success"] else "TLE / THẤT BẠI"
                status_col = COLOR_BTN_SUCCESS if res["Success"] else COLOR_BTN_DANGER

                surface.blit(font_small.render(algo_name, True, COLOR_TEXT_PRIMARY), (col_x[0], row_y))
                surface.blit(font_small.render(time_str, True, COLOR_TEXT_ACCENT), (col_x[1], row_y))
                surface.blit(font_small.render(assign_str, True, COLOR_TEXT_PRIMARY), (col_x[2], row_y))
                surface.blit(font_small.render(backtrack_str, True, COLOR_TEXT_PRIMARY), (col_x[3], row_y))
                surface.blit(font_small.render(nodes_str, True, COLOR_TEXT_PRIMARY), (col_x[4], row_y))
                surface.blit(font_small.render(status_str, True, status_col), (col_x[5], row_y))
        else:
            empty_msg = font_ui.render("Chưa có số liệu. Hãy bấm nút 'CHẠY ĐỐI ĐẦU 4 THUẬT TOÁN' ở trên!", True, COLOR_TEXT_MUTED)
            surface.blit(empty_msg, empty_msg.get_rect(center=table_rect.center))

        # 2. Biểu đồ thanh so sánh trực quan (Live Bar Chart)
        chart_rect = pygame.Rect(50, 435, 1180, 245)
        pygame.draw.rect(surface, COLOR_SURFACE, chart_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, chart_rect, width=1, border_radius=8)

        chart_title = font_small.render("BIỂU ĐỒ SO SÁNH THỜI GIAN THỰC THI (MILLISECONDS - CÀNG THẤP CÀNG TỐT):", True, COLOR_TEXT_ACCENT)
        surface.blit(chart_title, (70, 450))

        if self.results:
            bar_colors = [COLOR_BTN_PRIMARY, COLOR_BTN_SUCCESS, COLOR_BTN_DANGER, (243, 156, 18)]
            max_time = max(max(r["Time (ms)"] for r in self.results), 0.1)

            for idx, res in enumerate(self.results):
                bar_y = 485 + idx * 42
                algo_lbl = font_small.render(res["Algorithm"][:28], True, COLOR_TEXT_PRIMARY)
                surface.blit(algo_lbl, (70, bar_y))

                # Thanh bar
                bar_x = 340
                max_bar_w = 680
                val = res["Time (ms)"]
                bar_w = max(4, int((val / max_time) * max_bar_w))

                pygame.draw.rect(surface, COLOR_SURFACE_LIGHT, (bar_x, bar_y, max_bar_w, 24), border_radius=4)
                pygame.draw.rect(surface, bar_colors[idx % len(bar_colors)], (bar_x, bar_y, bar_w, 24), border_radius=4)

                val_surf = font_small.render(f"{val:.3f} ms", True, COLOR_TEXT_PRIMARY)
                surface.blit(val_surf, (bar_x + bar_w + 10, bar_y + 2))
        else:
            c_msg = font_small.render("Biểu đồ so sánh sẽ được dựng ngay sau khi chạy xong đối đầu.", True, COLOR_TEXT_MUTED)
            surface.blit(c_msg, (70, 520))

        # Thanh trạng thái dưới cùng
        status_surf = font_small.render(f"Trạng thái: {self.status_msg}", True, COLOR_TEXT_ACCENT)
        surface.blit(status_surf, (50, 695))
