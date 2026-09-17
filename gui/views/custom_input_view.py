"""
Custom Puzzle Input & Landmark Presets View.
Allows manually entering any 9x9 Sudoku puzzle or loading legendary mathematical benchmarks
(AI Escargot, Platinum Blonde, 17-Clue Minimum, Golden Nugget), verifying solvability,
and transferring the board to Visualizer or Play mode.
"""
import pygame
from typing import Optional, Tuple, Callable
from core.board import Board
from core.generator import count_solutions
from core.dataset import AI_ESCARGOT_REAL, PLATINUM_BLONDE_REAL, GORDON_ROYLE_17, GOLDEN_NUGGET
from gui.constants import (
    BOARD_X, BOARD_Y, BOARD_SIZE, CELL_SIZE, COLOR_BOARD_BG, COLOR_GRID_NORMAL,
    COLOR_GRID_BOX, COLOR_CELL_SELECTED, COLOR_NUM_FIXED, COLOR_SURFACE,
    COLOR_SURFACE_LIGHT, COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_TEXT_ACCENT,
    COLOR_BORDER, COLOR_BTN_PRIMARY, COLOR_BTN_SECONDARY, COLOR_BTN_SUCCESS,
    COLOR_BTN_DANGER
)
from gui.components import Button


class CustomInputView:
    def __init__(self, fonts: dict, on_export_puzzle: Optional[Callable[[str], None]] = None):
        self.fonts = fonts
        self.on_export_puzzle = on_export_puzzle
        self.board: Board = Board()
        self.selected_cell: Optional[Tuple[int, int]] = (0, 0)
        self.validation_result: str = "Nhập số hoặc chọn đề mẫu ở danh sách bên phải."

        # Controls
        btn_x = 640
        self.btn_escargot = Button(btn_x, 110, 275, 42, "AI Escargot (Arto Inkala 2006)", self._load_escargot, font_size=13, bg_color=COLOR_SURFACE_LIGHT)
        self.btn_platinum = Button(btn_x + 290, 110, 275, 42, "Platinum Blonde (Inkala 2010)", self._load_platinum, font_size=13, bg_color=COLOR_SURFACE_LIGHT)
        self.btn_17clue = Button(btn_x, 165, 275, 42, "17-Clue Minimum Puzzle", self._load_17clue, font_size=14, bg_color=COLOR_SURFACE_LIGHT)
        self.btn_golden = Button(btn_x + 290, 165, 275, 42, "Golden Nugget Benchmark", self._load_golden, font_size=14, bg_color=COLOR_SURFACE_LIGHT)

        self.btn_validate = Button(btn_x, 230, 275, 46, "KIỂM TRA NGHIỆM ĐỀ BÀI", self._validate_board, bg_color=COLOR_BTN_PRIMARY, text_color=(20, 20, 30), font_size=14)
        self.btn_clear = Button(btn_x + 290, 230, 275, 46, "XÓA TRẮNG BÀN CỜ", self._clear_board, bg_color=COLOR_BTN_DANGER, text_color=(20, 20, 30), font_size=14)

        self.btn_send_visualizer = Button(btn_x, 300, 565, 46, "NẠP ĐỀ NÀY VÀO CHẾ ĐỘ VISUALIZER", self._send_to_visualizer, bg_color=COLOR_BTN_SUCCESS, text_color=(20, 20, 30), font_size=15)

    def _load_escargot(self):
        self.board = Board.from_string(AI_ESCARGOT_REAL)
        self.validation_result = "Đã nạp AI Escargot (Được thiết kế để vô hiệu hóa Backtracking thuần)."

    def _load_platinum(self):
        self.board = Board.from_string(PLATINUM_BLONDE_REAL)
        self.validation_result = "Đã nạp Platinum Blonde (Độ khó 11 sao của Arto Inkala)."

    def _load_17clue(self):
        self.board = Board.from_string(GORDON_ROYLE_17)
        self.validation_result = "Đã nạp 17-Clue (Giới hạn tối thiểu lý thuyết để Sudoku có nghiệm duy nhất)."

    def _load_golden(self):
        self.board = Board.from_string(GOLDEN_NUGGET)
        self.validation_result = "Đã nạp Golden Nugget (Thử thách siêu cấp)."

    def _clear_board(self):
        self.board = Board()
        self.validation_result = "Đã xóa trắng bàn cờ. Bạn có thể tự nhập đề."

    def _validate_board(self):
        if not self.board.is_valid_board():
            self.validation_result = "ĐỀ BÀI KHÔNG HỢP LỆ! Có số trùng nhau trên cùng hàng, cột hoặc khối!"
            return

        cloned = self.board.copy()
        sols = count_solutions(cloned, limit=2)
        if sols == 0:
            self.validation_result = "VÔ NGHIỆM! Đề bài này không thể giải được."
        elif sols == 1:
            self.validation_result = "HỢP LỆ & NGHIỆM DUY NHẤT! Đề bài đạt tiêu chuẩn giải thuật."
        else:
            self.validation_result = "ĐA NGHIỆM! Đề bài có từ 2 nghiệm trở lên (chưa đủ dữ kiện)."

    def _send_to_visualizer(self):
        if self.on_export_puzzle:
            self.on_export_puzzle(self.board.to_string())
            self.validation_result = "ĐÃ GỬI ĐỀ SANG TAB VISUALIZER! Hãy bấm sang tab Visualizer để xem giải."

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if self.selected_cell:
                r, c = self.selected_cell
                if event.key in (pygame.K_1, pygame.K_KP1): self.board.set(r, c, 1)
                elif event.key in (pygame.K_2, pygame.K_KP2): self.board.set(r, c, 2)
                elif event.key in (pygame.K_3, pygame.K_KP3): self.board.set(r, c, 3)
                elif event.key in (pygame.K_4, pygame.K_KP4): self.board.set(r, c, 4)
                elif event.key in (pygame.K_5, pygame.K_KP5): self.board.set(r, c, 5)
                elif event.key in (pygame.K_6, pygame.K_KP6): self.board.set(r, c, 6)
                elif event.key in (pygame.K_7, pygame.K_KP7): self.board.set(r, c, 7)
                elif event.key in (pygame.K_8, pygame.K_KP8): self.board.set(r, c, 8)
                elif event.key in (pygame.K_9, pygame.K_KP9): self.board.set(r, c, 9)
                elif event.key in (pygame.K_0, pygame.K_KP0, pygame.K_BACKSPACE, pygame.K_DELETE): self.board.clear(r, c)
                # Điều hướng mũi tên bàn phím
                elif event.key == pygame.K_UP: self.selected_cell = (max(0, r - 1), c)
                elif event.key == pygame.K_DOWN: self.selected_cell = (min(8, r + 1), c)
                elif event.key == pygame.K_LEFT: self.selected_cell = (r, max(0, c - 1))
                elif event.key == pygame.K_RIGHT: self.selected_cell = (r, min(8, c + 1))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if BOARD_X <= mx <= BOARD_X + BOARD_SIZE and BOARD_Y <= my <= BOARD_Y + BOARD_SIZE:
                c = (mx - BOARD_X) // CELL_SIZE
                r = (my - BOARD_Y) // CELL_SIZE
                if 0 <= r < 9 and 0 <= c < 9:
                    self.selected_cell = (r, c)

        self.btn_escargot.handle_event(event)
        self.btn_platinum.handle_event(event)
        self.btn_17clue.handle_event(event)
        self.btn_golden.handle_event(event)
        self.btn_validate.handle_event(event)
        self.btn_clear.handle_event(event)
        self.btn_send_visualizer.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        font_num = self.fonts["number"]
        font_small = self.fonts["small"]
        font_ui = self.fonts["ui"]

        # 1. Bàn cờ
        pygame.draw.rect(surface, COLOR_BOARD_BG, (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), border_radius=6)

        for r in range(9):
            for c in range(9):
                cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = self.board.get(r, c)

                if self.selected_cell == (r, c):
                    pygame.draw.rect(surface, COLOR_CELL_SELECTED, cell_rect)

                if val != 0:
                    txt = font_num.render(str(val), True, COLOR_NUM_FIXED)
                    surface.blit(txt, txt.get_rect(center=cell_rect.center))

        for i in range(10):
            thickness = 3 if (i % 3 == 0) else 1
            color = COLOR_GRID_BOX if (i % 3 == 0) else COLOR_GRID_NORMAL
            pygame.draw.line(surface, color, (BOARD_X, BOARD_Y + i * CELL_SIZE), (BOARD_X + BOARD_SIZE, BOARD_Y + i * CELL_SIZE), thickness)
            pygame.draw.line(surface, color, (BOARD_X + i * CELL_SIZE, BOARD_Y), (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_SIZE), thickness)

        # 2. Side panel
        side_rect = pygame.Rect(620, BOARD_Y, 610, BOARD_SIZE)
        pygame.draw.rect(surface, COLOR_SURFACE, side_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, side_rect, width=1, border_radius=8)

        title_surf = self.fonts["title"].render("TỰ NHẬP ĐỀ & NẠP ĐỀ MẪU HỌC THUẬT", True, COLOR_TEXT_ACCENT)
        surface.blit(title_surf, (640, 70))

        self.btn_escargot.draw(surface, font_small)
        self.btn_platinum.draw(surface, font_small)
        self.btn_17clue.draw(surface, font_small)
        self.btn_golden.draw(surface, font_small)
        self.btn_validate.draw(surface, font_small)
        self.btn_clear.draw(surface, font_small)
        self.btn_send_visualizer.draw(surface, font_ui)

        # Hộp thông báo kết quả kiểm tra
        res_rect = pygame.Rect(640, 375, 565, 80)
        pygame.draw.rect(surface, COLOR_SURFACE_LIGHT, res_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, res_rect, width=1, border_radius=6)
        res_txt = font_small.render(self.validation_result, True, COLOR_TEXT_ACCENT)
        surface.blit(res_txt, (655, 405))

        # Thống kê số lượng ô đã điền
        clue_count = 81 - self.board.count_empty_cells()
        c_surf = font_ui.render(f"Số ô đã điền: {clue_count}/81   |   Số ô trống: {81 - clue_count}", True, COLOR_TEXT_PRIMARY)
        surface.blit(c_surf, (640, 480))

        # Hướng dẫn
        guide_lines = [
            "• Dùng chuột click ô bất kỳ hoặc dùng phím mũi tên di chuyển.",
            "• Gõ phím số 1..9 để điền số, gõ 0 / Backspace / Del để xóa.",
            "• Bấm 'KIỂM TRA NGHIỆM' để giải thuật đếm số nghiệm duy nhất.",
            "• Bấm 'NẠP ĐỀ VÀO VISUALIZER' để quan sát thuật toán giải bài này."
        ]
        gy = 515
        for g in guide_lines:
            surface.blit(font_small.render(g, True, COLOR_TEXT_MUTED), (640, gy))
            gy += 22
