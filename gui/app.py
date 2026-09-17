"""
Master Pygame Application managing 60 FPS loop, font loading with UTF-8 support,
navigation TabBar, and event routing to the respective views.
"""
import pygame
import sys
from gui.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLOR_BG, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_ACCENT
)
from gui.components import TabBar
from gui.views.play_view import PlayView
from gui.views.visualizer_view import VisualizerView
from gui.views.benchmark_view import BenchmarkView
from gui.views.custom_input_view import CustomInputView


class SudokuApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Phân Tích & Thiết Kế Giải Thuật - Sudoku Solver & Visualizer")
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Khởi tạo Fonts hệ thống (Ưu tiên Segoe UI trên Windows để hiển thị tiếng Việt hoàn hảo)
        self.fonts = self._init_fonts()

        # TabBar điều hướng
        tab_names = [
            "1. Tự Chơi (Play)",
            "2. Trực Quan Hóa (Visualizer)",
            "3. Đối Sánh Hiệu Năng (Benchmark)",
            "4. Tự Nhập Đề (Custom Input)"
        ]
        self.tab_bar = TabBar(50, 15, 1180, 42, tab_names, self._on_tab_change)

        # Các Views
        self.play_view = PlayView(self.fonts)
        self.visualizer_view = VisualizerView(self.fonts)
        self.benchmark_view = BenchmarkView(self.fonts)
        self.custom_input_view = CustomInputView(self.fonts, on_export_puzzle=self._on_export_to_visualizer)

        self.current_tab = 0
        self.views = [
            self.play_view,
            self.visualizer_view,
            self.benchmark_view,
            self.custom_input_view
        ]

    def _init_fonts(self) -> dict:
        font_candidates = ["segoeui", "arial", "helvetica", "tahoma"]
        base_font = None
        for name in font_candidates:
            matched = pygame.font.match_font(name)
            if matched:
                base_font = matched
                break

        def make_font(size: int, bold: bool = False):
            if base_font:
                f = pygame.font.Font(base_font, size)
                f.set_bold(bold)
                return f
            return pygame.font.SysFont("arial", size, bold=bold)

        return {
            "title": make_font(22, bold=True),
            "ui": make_font(18, bold=True),
            "number": make_font(28, bold=True),
            "small": make_font(14, bold=False),
            "tiny": make_font(11, bold=False),
        }

    def _on_tab_change(self, index: int):
        self.current_tab = index

    def _on_export_to_visualizer(self, puzzle_str: str):
        self.visualizer_view.current_puzzle_str = puzzle_str
        self.visualizer_view._reset()
        self.current_tab = 1
        self.tab_bar.selected_index = 1

    def run(self):
        while self.is_running:
            # 1. Xử lý Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    break
                
                # TabBar event
                if self.tab_bar.handle_event(event):
                    continue

                # View event
                self.views[self.current_tab].handle_event(event)

            # 2. Update logic (chủ yếu cho Visualizer animation)
            if self.current_tab == 1:
                self.visualizer_view.update()

            # 3. Vẽ Render
            self.screen.fill(COLOR_BG)

            # Vẽ TabBar điều hướng
            self.tab_bar.draw(self.screen, self.fonts["ui"])

            # Vẽ View hiện tại
            self.views[self.current_tab].draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)
