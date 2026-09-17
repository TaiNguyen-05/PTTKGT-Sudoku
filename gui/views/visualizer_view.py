"""
Algorithm Step-by-Step Visualizer View.
Animates the state-space search of each algorithm with adjustable speed,
highlighting cell attempts (yellow), backtracks (red-coral), and confirmed digits (green).
"""
import pygame
import time
from typing import Optional, Tuple, Dict, Any
from core.board import Board
from core.dataset import SAMPLE_PUZZLES, AI_ESCARGOT_REAL
from algorithms.base_solver import BaseSolver
from algorithms.naive_backtracking import NaiveBacktrackingSolver
from algorithms.heuristic_backtracking import HeuristicBacktrackingSolver
from algorithms.dancing_links import DancingLinksSolver
from algorithms.simulated_annealing import SimulatedAnnealingSolver
from gui.constants import (
    BOARD_X, BOARD_Y, BOARD_SIZE, CELL_SIZE, COLOR_BOARD_BG, COLOR_GRID_NORMAL,
    COLOR_GRID_BOX, COLOR_TRY, COLOR_BACKTRACK, COLOR_CONFIRM, COLOR_NUM_FIXED,
    COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT, COLOR_BORDER, COLOR_BTN_PRIMARY, COLOR_BTN_SECONDARY,
    COLOR_BTN_SUCCESS, COLOR_BTN_DANGER
)
from gui.components import Button, Slider


class VisualizerView:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.current_puzzle_str = SAMPLE_PUZZLES["Easy"]["Easy 1 (38 clues)"]
        self.board: Board = Board.from_string(self.current_puzzle_str)
        self.active_cell: Optional[Tuple[int, int]] = None
        self.active_action: str = ""
        
        # Solver & Generator
        self.solvers = {
            "Naive Backtracking": NaiveBacktrackingSolver(),
            "Heuristic CSP (MRV)": HeuristicBacktrackingSolver(),
            "Dancing Links (DLX)": DancingLinksSolver(),
            "Simulated Annealing": SimulatedAnnealingSolver(max_iterations=10000)
        }
        self.selected_algo_name = "Dancing Links (DLX)"
        self.solver: BaseSolver = self.solvers[self.selected_algo_name]
        self.generator = None
        
        # Trạng thái Animation
        self.is_running = False
        self.is_finished = False
        self.speed_fps = 30  # Số bước mỗi giây
        self.steps_per_frame = 1
        self.step_count = 0
        self.backtrack_count = 0
        self.start_time = 0.0
        self.elapsed_ms = 0.0
        self.status_text = "Sẵn sàng chạy visualizer."

        # Khởi tạo Controls
        btn_x = 640
        
        # Chọn thuật toán
        self.btn_algos = []
        algo_names = list(self.solvers.keys())
        for idx, name in enumerate(algo_names):
            bx = btn_x + (idx % 2) * 290
            by = 105 + (idx // 2) * 45
            btn = Button(
                bx, by, 275, 38, name,
                lambda n=name: self._select_algorithm(n),
                bg_color=COLOR_BTN_PRIMARY if name == self.selected_algo_name else COLOR_SURFACE_LIGHT,
                text_color=(20, 20, 30) if name == self.selected_algo_name else COLOR_TEXT_PRIMARY,
                font_size=15
            )
            self.btn_algos.append((name, btn))

        # Chọn câu đố
        self.btn_puzzles = [
            Button(btn_x, 205, 105, 35, "Dễ", lambda: self._load_preset("Easy", "Easy 1 (38 clues)"), font_size=14),
            Button(btn_x + 115, 205, 105, 35, "Vừa", lambda: self._load_preset("Medium", "Medium 1 (30 clues)"), font_size=14),
            Button(btn_x + 230, 205, 105, 35, "Khó", lambda: self._load_preset("Hard", "Hard 1 (26 clues)"), font_size=14),
            Button(btn_x + 345, 205, 105, 35, "Chuyên gia", lambda: self._load_preset("Expert / Nightmare", "Expert 1 (23 clues)"), font_size=14),
            Button(btn_x + 460, 205, 115, 35, "AI Escargot", self._load_escargot, font_size=13, bg_color=COLOR_BTN_DANGER, text_color=(20, 20, 30)),
        ]

        # Nút điều khiển Animation (Play, Pause, Step, Reset)
        self.btn_play = Button(btn_x, 260, 135, 42, "Chạy (Run)", self._start, bg_color=COLOR_BTN_SUCCESS, text_color=(20, 20, 30))
        self.btn_pause = Button(btn_x + 145, 260, 135, 42, "Tạm dừng", self._pause, bg_color=COLOR_BTN_SECONDARY)
        self.btn_step = Button(btn_x + 290, 260, 135, 42, "Đi 1 bước", self._step_once, bg_color=COLOR_BTN_SECONDARY)
        self.btn_reset = Button(btn_x + 435, 260, 140, 42, "Đặt lại (Reset)", self._reset, bg_color=COLOR_BTN_SECONDARY)

        # Thanh trượt tốc độ
        self.slider_speed = Slider(btn_x, 345, 575, 12, 1, 300, 30, "Tốc độ hiển thị", self._set_speed)

    def _select_algorithm(self, name: str):
        self.selected_algo_name = name
        self.solver = self.solvers[name]
        for n, btn in self.btn_algos:
            if n == name:
                btn.bg_color = COLOR_BTN_PRIMARY
                btn.text_color = (20, 20, 30)
            else:
                btn.bg_color = COLOR_SURFACE_LIGHT
                btn.text_color = COLOR_TEXT_PRIMARY
        self._reset()
        self.status_text = f"Đã chọn: {name}."

    def _load_preset(self, cat: str, name: str):
        self.current_puzzle_str = SAMPLE_PUZZLES[cat][name]
        self._reset()
        self.status_text = f"Đã tải câu đố: {name}."

    def _load_escargot(self):
        self.current_puzzle_str = AI_ESCARGOT_REAL
        self._reset()
        self.status_text = "Đã tải bài toán khó nhất thế giới (AI Escargot 2006)!"

    def _set_speed(self, val: float):
        self.speed_fps = int(val)
        if self.speed_fps > 100:
            self.steps_per_frame = (self.speed_fps // 60) + 1
        else:
            self.steps_per_frame = 1

    def _start(self):
        if self.is_finished:
            self._reset()
        if self.generator is None:
            self.board = Board.from_string(self.current_puzzle_str)
            self.generator = self.solver.solve_stepwise(self.board)
            self.start_time = time.perf_counter()
        self.is_running = True
        self.status_text = f"Đang chạy {self.selected_algo_name}..."

    def _pause(self):
        self.is_running = False
        self.status_text = "Đã tạm dừng visualizer."

    def _reset(self):
        self.is_running = False
        self.is_finished = False
        self.generator = None
        self.board = Board.from_string(self.current_puzzle_str)
        self.active_cell = None
        self.active_action = ""
        self.step_count = 0
        self.backtrack_count = 0
        self.elapsed_ms = 0.0
        self.status_text = "Đã đặt lại trạng thái bàn cờ."

    def _step_once(self):
        if self.generator is None:
            self.board = Board.from_string(self.current_puzzle_str)
            self.generator = self.solver.solve_stepwise(self.board)
            self.start_time = time.perf_counter()

        try:
            r, c, val, action = next(self.generator)
            self.step_count += 1
            self.active_cell = (r, c)
            self.active_action = action
            if action == "BACKTRACK":
                self.backtrack_count += 1
            self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0
        except StopIteration as e:
            self.is_running = False
            self.is_finished = True
            success = e.value if e.value is not None else True
            self.status_text = "THÀNH CÔNG! ĐÃ GIẢI XONG!" if success else "VÔ NGHIỆM!"

    def update(self) -> None:
        """Thực thi các bước animation theo tốc độ đã cấu hình."""
        if not self.is_running or self.is_finished or self.generator is None:
            return

        for _ in range(self.steps_per_frame):
            try:
                r, c, val, action = next(self.generator)
                self.step_count += 1
                self.active_cell = (r, c)
                self.active_action = action
                if action == "BACKTRACK":
                    self.backtrack_count += 1
            except StopIteration as e:
                self.is_running = False
                self.is_finished = True
                self.active_cell = None
                success = e.value if e.value is not None else True
                self.status_text = "THÀNH CÔNG! ĐÃ GIẢI XONG BÀN CỜ!" if success else "VÔ NGHIỆM!"
                break

        if self.start_time > 0:
            self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0

    def handle_event(self, event: pygame.event.Event) -> None:
        for _, btn in self.btn_algos:
            btn.handle_event(event)
        for btn in self.btn_puzzles:
            btn.handle_event(event)
        self.btn_play.handle_event(event)
        self.btn_pause.handle_event(event)
        self.btn_step.handle_event(event)
        self.btn_reset.handle_event(event)
        self.slider_speed.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        font_num = self.fonts["number"]
        font_small = self.fonts["small"]
        font_ui = self.fonts["ui"]

        # 1. Vẽ bàn cờ Sudoku
        pygame.draw.rect(surface, COLOR_BOARD_BG, (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), border_radius=6)

        for r in range(9):
            for c in range(9):
                cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = self.board.get(r, c)

                # Tô màu ô đang được thuật toán thao tác
                if self.active_cell == (r, c):
                    if self.active_action == "TRY":
                        pygame.draw.rect(surface, COLOR_TRY, cell_rect)
                    elif self.active_action == "BACKTRACK":
                        pygame.draw.rect(surface, COLOR_BACKTRACK, cell_rect)
                    elif self.active_action == "CONFIRM":
                        pygame.draw.rect(surface, COLOR_CONFIRM, cell_rect)

                # Vẽ số
                if val != 0:
                    if self.board.is_fixed(r, c):
                        txt_color = COLOR_NUM_FIXED
                    elif self.active_cell == (r, c) and self.active_action in ("TRY", "BACKTRACK", "CONFIRM"):
                        txt_color = (20, 20, 30)  # Chữ đen trên nền màu highlight
                    else:
                        txt_color = COLOR_TEXT_ACCENT

                    txt = font_num.render(str(val), True, txt_color)
                    surface.blit(txt, txt.get_rect(center=cell_rect.center))

        # Lưới bàn cờ
        for i in range(10):
            thickness = 3 if (i % 3 == 0) else 1
            color = COLOR_GRID_BOX if (i % 3 == 0) else COLOR_GRID_NORMAL
            pygame.draw.line(surface, color, (BOARD_X, BOARD_Y + i * CELL_SIZE), (BOARD_X + BOARD_SIZE, BOARD_Y + i * CELL_SIZE), thickness)
            pygame.draw.line(surface, color, (BOARD_X + i * CELL_SIZE, BOARD_Y), (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_SIZE), thickness)

        # 2. Bảng điều khiển thuật toán & Metrics bên phải
        side_rect = pygame.Rect(620, BOARD_Y, 610, BOARD_SIZE)
        pygame.draw.rect(surface, COLOR_SURFACE, side_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, side_rect, width=1, border_radius=8)

        # Tiêu đề
        title_surf = self.fonts["title"].render("TRỰC QUAN HÓA THUẬT TOÁN (VISUALIZER)", True, COLOR_TEXT_ACCENT)
        surface.blit(title_surf, (640, 70))

        # Vẽ các nút thuật toán & câu đố & điều khiển
        for _, btn in self.btn_algos:
            btn.draw(surface, font_small)
        for btn in self.btn_puzzles:
            btn.draw(surface, font_small)

        self.btn_play.draw(surface, font_small)
        self.btn_pause.draw(surface, font_small)
        self.btn_step.draw(surface, font_small)
        self.btn_reset.draw(surface, font_small)
        self.slider_speed.draw(surface, font_small)

        # Bảng đo lường số liệu thời gian thực (Live Metrics Panel)
        metrics_rect = pygame.Rect(640, 385, 570, 160)
        pygame.draw.rect(surface, COLOR_SURFACE_LIGHT, metrics_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, metrics_rect, width=1, border_radius=8)

        m_y = 398
        m_title = font_ui.render("CHỈ SỐ ĐO LƯỜNG THỰC NGHIỆM (EMPIRICAL METRICS):", True, COLOR_TEXT_ACCENT)
        surface.blit(m_title, (655, m_y))

        m_y += 30
        line1 = font_small.render(f"• Thuật toán đang chạy: {self.selected_algo_name}", True, COLOR_TEXT_PRIMARY)
        surface.blit(line1, (655, m_y))

        m_y += 24
        line2 = font_small.render(f"• Số bước thực thi (Steps): {self.step_count:,}   |   Số lần quay lui (Backtracks): {self.backtrack_count:,}", True, COLOR_TEXT_PRIMARY)
        surface.blit(line2, (655, m_y))

        m_y += 24
        line3 = font_small.render(f"• Thời gian thực tế: {self.elapsed_ms:.2f} ms   |   Hành động hiện tại: {self.active_action or 'Chờ lệnh'}", True, COLOR_TEXT_PRIMARY)
        surface.blit(line3, (655, m_y))

        m_y += 24
        status_color = COLOR_BTN_SUCCESS if self.is_finished else COLOR_TEXT_ACCENT
        line4 = font_small.render(f"• Trạng thái: {self.status_text}", True, status_color)
        surface.blit(line4, (655, m_y))

        # Chú thích màu sắc (Legend)
        leg_y = 560
        pygame.draw.rect(surface, COLOR_TRY, (640, leg_y, 16, 16), border_radius=3)
        surface.blit(font_small.render("Đang thử (Try)", True, COLOR_TEXT_MUTED), (665, leg_y - 2))

        pygame.draw.rect(surface, COLOR_BACKTRACK, (780, leg_y, 16, 16), border_radius=3)
        surface.blit(font_small.render("Quay lui (Backtrack)", True, COLOR_TEXT_MUTED), (805, leg_y - 2))

        pygame.draw.rect(surface, COLOR_CONFIRM, (950, leg_y, 16, 16), border_radius=3)
        surface.blit(font_small.render("Đã chốt (Confirmed)", True, COLOR_TEXT_MUTED), (975, leg_y - 2))
