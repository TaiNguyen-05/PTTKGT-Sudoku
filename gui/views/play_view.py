"""
Interactive Playable Sudoku Mode.
Allows playing Sudoku with keyboard/mouse inputs, pencil draft notes, conflict validation, hints, and undo.
"""
import pygame
import time
from typing import Optional, Tuple, Set, List
from core.board import Board
from core.generator import generate_sudoku
from algorithms.dancing_links import DancingLinksSolver
from gui.constants import (
    BOARD_X, BOARD_Y, BOARD_SIZE, CELL_SIZE, COLOR_BOARD_BG, COLOR_GRID_NORMAL,
    COLOR_GRID_BOX, COLOR_CELL_SELECTED, COLOR_CELL_SAME_VAL, COLOR_NUM_FIXED,
    COLOR_NUM_USER, COLOR_NUM_PENCIL, COLOR_CONFLICT, COLOR_SURFACE, COLOR_SURFACE_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_TEXT_ACCENT, COLOR_BORDER,
    COLOR_BTN_PRIMARY, COLOR_BTN_SECONDARY, COLOR_BTN_SUCCESS, COLOR_BTN_DANGER
)
from gui.components import Button


class PlayView:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.board: Board = generate_sudoku("Medium")
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.pencil_mode: bool = False
        self.pencil_notes: List[List[Set[int]]] = [[set() for _ in range(9)] for _ in range(9)]
        self.history: List[Tuple[int, int, int]] = []
        
        self.start_time = time.time()
        self.elapsed_time = 0
        self.is_game_won = False
        self.message = "Chúc bạn chơi vui vẻ! Nhấn P để bật/tắt chế độ bút chì ghi chú."

        # Khởi tạo các nút điều khiển
        btn_x = 640
        self.btn_new_easy = Button(btn_x, 110, 130, 38, "Dễ (Easy)", lambda: self._new_game("Easy"), bg_color=COLOR_SURFACE_LIGHT)
        self.btn_new_medium = Button(btn_x + 145, 110, 130, 38, "Vừa (Medium)", lambda: self._new_game("Medium"), bg_color=COLOR_SURFACE_LIGHT)
        self.btn_new_hard = Button(btn_x + 290, 110, 130, 38, "Khó (Hard)", lambda: self._new_game("Hard"), bg_color=COLOR_SURFACE_LIGHT)
        self.btn_new_expert = Button(btn_x + 435, 110, 130, 38, "Chuyên gia", lambda: self._new_game("Expert"), bg_color=COLOR_SURFACE_LIGHT)

        self.btn_pencil = Button(btn_x, 170, 180, 42, "Bút chì: TẮT", self._toggle_pencil, bg_color=COLOR_BTN_SECONDARY)
        self.btn_undo = Button(btn_x + 195, 170, 120, 42, "Hoàn tác", self._undo, bg_color=COLOR_BTN_SECONDARY)
        self.btn_hint = Button(btn_x + 330, 170, 110, 42, "Gợi ý", self._give_hint, bg_color=COLOR_BTN_PRIMARY, text_color=(20, 20, 30))
        self.btn_auto_solve = Button(btn_x + 455, 170, 110, 42, "Giải nhanh", self._auto_solve, bg_color=COLOR_BTN_SUCCESS, text_color=(20, 20, 30))

        # Numpad buttons (1..9)
        self.numpad_btns: List[Button] = []
        for num in range(1, 10):
            nx = btn_x + ((num - 1) % 5) * 75
            ny = 235 + ((num - 1) // 5) * 55
            self.numpad_btns.append(
                Button(nx, ny, 65, 45, str(num), lambda n=num: self._input_number(n), font_size=20)
            )
        # Nút xóa số
        self.btn_erase = Button(btn_x + 300, 290, 140, 45, "Xóa ô (Del)", self._erase_number, bg_color=COLOR_BTN_DANGER, text_color=(20, 20, 30))

    def _new_game(self, diff: str):
        self.board = generate_sudoku(diff)
        self.pencil_notes = [[set() for _ in range(9)] for _ in range(9)]
        self.history.clear()
        self.selected_cell = None
        self.start_time = time.time()
        self.is_game_won = False
        self.message = f"Đã tạo ván mới cấp độ {diff}!"

    def _toggle_pencil(self):
        self.pencil_mode = not self.pencil_mode
        self.btn_pencil.text = f"Bút chì: {'BẬT' if self.pencil_mode else 'TẮT'}"
        self.btn_pencil.bg_color = COLOR_BTN_PRIMARY if self.pencil_mode else COLOR_BTN_SECONDARY
        self.btn_pencil.text_color = (20, 20, 30) if self.pencil_mode else COLOR_TEXT_PRIMARY

    def _input_number(self, val: int):
        if not self.selected_cell or self.is_game_won:
            return

        r, c = self.selected_cell
        if self.board.is_fixed(r, c):
            return

        if self.pencil_mode:
            if val in self.pencil_notes[r][c]:
                self.pencil_notes[r][c].remove(val)
            else:
                self.pencil_notes[r][c].add(val)
        else:
            old_val = self.board.get(r, c)
            self.history.append((r, c, old_val))
            self.board.set(r, c, val)
            self.pencil_notes[r][c].clear()

            # Kiểm tra chiến thắng
            if self.board.is_solved():
                self.is_game_won = True
                self.message = "CHÚC MỪNG BẠN ĐÃ GIẢI HOÀN THÀNH BÀN CỜ!"
            elif not self.board.is_valid_placement(r, c, val):
                self.message = f"Cảnh báo: Số {val} bị xung đột hàng/cột/khối!"
            else:
                self.message = f"Đã điền số {val} vào ô ({r+1}, {c+1})."

    def _erase_number(self):
        if not self.selected_cell or self.is_game_won:
            return
        r, c = self.selected_cell
        if not self.board.is_fixed(r, c):
            old_val = self.board.get(r, c)
            self.history.append((r, c, old_val))
            self.board.clear(r, c)
            self.pencil_notes[r][c].clear()

    def _undo(self):
        if self.history:
            r, c, old_val = self.history.pop()
            self.board.set(r, c, old_val)
            self.selected_cell = (r, c)

    def _give_hint(self):
        """Dùng Dancing Links giải nghiệm chuẩn rồi điền 1 ô gợi ý."""
        if self.is_game_won:
            return
        clone = self.board.copy()
        solver = DancingLinksSolver()
        success, _ = solver.solve(clone)
        if success:
            empty_cells = self.board.get_all_empty_cells()
            if empty_cells:
                # Ưu tiên gợi ý vào ô đang chọn nếu ô đó trống
                target = self.selected_cell if (self.selected_cell and self.board.get(*self.selected_cell) == 0) else empty_cells[0]
                r, c = target
                correct_val = clone.get(r, c)
                self.board.set(r, c, correct_val)
                self.selected_cell = (r, c)
                self.message = f"Gợi ý: Điền số {correct_val} vào ô ({r+1}, {c+1})!"
                if self.board.is_solved():
                    self.is_game_won = True
                    self.message = "CHÚC MỪNG BẠN ĐÃ GIẢI HOÀN THÀNH BÀN CỜ!"

    def _auto_solve(self):
        solver = DancingLinksSolver()
        success, metrics = solver.solve(self.board)
        if success:
            self.is_game_won = True
            self.message = f"Đã giải tự động bằng DLX trong {metrics.execution_time_ms:.2f} ms!"

    def handle_event(self, event: pygame.event.Event) -> None:
        # Bàn phím
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1): self._input_number(1)
            elif event.key in (pygame.K_2, pygame.K_KP2): self._input_number(2)
            elif event.key in (pygame.K_3, pygame.K_KP3): self._input_number(3)
            elif event.key in (pygame.K_4, pygame.K_KP4): self._input_number(4)
            elif event.key in (pygame.K_5, pygame.K_KP5): self._input_number(5)
            elif event.key in (pygame.K_6, pygame.K_KP6): self._input_number(6)
            elif event.key in (pygame.K_7, pygame.K_KP7): self._input_number(7)
            elif event.key in (pygame.K_8, pygame.K_KP8): self._input_number(8)
            elif event.key in (pygame.K_9, pygame.K_KP9): self._input_number(9)
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE): self._erase_number()
            elif event.key == pygame.K_p: self._toggle_pencil()
            elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL): self._undo()

        # Chuột bấm vào bàn cờ
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if BOARD_X <= mx <= BOARD_X + BOARD_SIZE and BOARD_Y <= my <= BOARD_Y + BOARD_SIZE:
                c = (mx - BOARD_X) // CELL_SIZE
                r = (my - BOARD_Y) // CELL_SIZE
                if 0 <= r < 9 and 0 <= c < 9:
                    self.selected_cell = (r, c)

        # Xử lý các nút bấm
        self.btn_new_easy.handle_event(event)
        self.btn_new_medium.handle_event(event)
        self.btn_new_hard.handle_event(event)
        self.btn_new_expert.handle_event(event)
        self.btn_pencil.handle_event(event)
        self.btn_undo.handle_event(event)
        self.btn_hint.handle_event(event)
        self.btn_auto_solve.handle_event(event)
        self.btn_erase.handle_event(event)
        for btn in self.numpad_btns:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        font_num = self.fonts["number"]
        font_small = self.fonts["small"]
        font_ui = self.fonts["ui"]

        # Cập nhật thời gian
        if not self.is_game_won:
            self.elapsed_time = int(time.time() - self.start_time)
        mins = self.elapsed_time // 60
        secs = self.elapsed_time % 60

        # 1. Vẽ bàn cờ Sudoku
        pygame.draw.rect(surface, COLOR_BOARD_BG, (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), border_radius=6)

        # Highlight ô cùng số với ô đang chọn
        selected_val = 0
        if self.selected_cell:
            sr, sc = self.selected_cell
            selected_val = self.board.get(sr, sc)

        for r in range(9):
            for c in range(9):
                cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = self.board.get(r, c)

                # Nền ô được chọn
                if self.selected_cell == (r, c):
                    pygame.draw.rect(surface, COLOR_CELL_SELECTED, cell_rect)
                elif selected_val > 0 and val == selected_val:
                    pygame.draw.rect(surface, COLOR_CELL_SAME_VAL, cell_rect)

                # Số trong ô
                if val != 0:
                    if self.board.is_fixed(r, c):
                        txt_color = COLOR_NUM_FIXED
                    elif not self.board.is_valid_placement(r, c, val):
                        txt_color = COLOR_CONFLICT
                    else:
                        txt_color = COLOR_NUM_USER

                    txt = font_num.render(str(val), True, txt_color)
                    surface.blit(txt, txt.get_rect(center=cell_rect.center))
                else:
                    # Vẽ các số ghi chú bút chì
                    notes = self.pencil_notes[r][c]
                    if notes:
                        for pnum in notes:
                            pr = (pnum - 1) // 3
                            pc = (pnum - 1) % 3
                            px = cell_rect.x + pc * 18 + 9
                            py = cell_rect.y + pr * 18 + 9
                            ptxt = font_small.render(str(pnum), True, COLOR_NUM_PENCIL)
                            surface.blit(ptxt, ptxt.get_rect(center=(px, py)))

        # Lưới bàn cờ (mảnh và đậm)
        for i in range(10):
            thickness = 3 if (i % 3 == 0) else 1
            color = COLOR_GRID_BOX if (i % 3 == 0) else COLOR_GRID_NORMAL
            # Kẻ ngang
            pygame.draw.line(surface, color, (BOARD_X, BOARD_Y + i * CELL_SIZE), (BOARD_X + BOARD_SIZE, BOARD_Y + i * CELL_SIZE), thickness)
            # Kẻ dọc
            pygame.draw.line(surface, color, (BOARD_X + i * CELL_SIZE, BOARD_Y), (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_SIZE), thickness)

        # 2. Bảng điều khiển bên phải (Side Panel)
        side_panel_rect = pygame.Rect(620, BOARD_Y, 610, BOARD_SIZE)
        pygame.draw.rect(surface, COLOR_SURFACE, side_panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, side_panel_rect, width=1, border_radius=8)

        # Tiêu đề panel
        title_surf = self.fonts["title"].render("CHẾ ĐỘ TỰ CHƠI (PLAYER MODE)", True, COLOR_TEXT_ACCENT)
        surface.blit(title_surf, (640, 70))

        # Đồng hồ đếm giờ & Ô trống
        empty_count = self.board.count_empty_cells()
        timer_surf = font_ui.render(f"Thời gian: {mins:02d}:{secs:02d}   |   Ô trống còn lại: {empty_count}", True, COLOR_TEXT_PRIMARY)
        surface.blit(timer_surf, (640, 120 + 245))

        # Khung thông báo hướng dẫn
        msg_rect = pygame.Rect(640, 420, 570, 75)
        pygame.draw.rect(surface, COLOR_SURFACE_LIGHT, msg_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, msg_rect, width=1, border_radius=6)
        msg_surf = font_small.render(self.message, True, COLOR_TEXT_ACCENT if not self.is_game_won else COLOR_BTN_SUCCESS)
        surface.blit(msg_surf, (655, 445))

        # Hướng dẫn phím tắt
        tips = font_small.render("Phím tắt: 1-9 (điền số), Del/Backspace (xóa), P (bật/tắt bút chì), Ctrl+Z (hoàn tác)", True, COLOR_TEXT_MUTED)
        surface.blit(tips, (640, 510))

        # Vẽ các nút
        self.btn_new_easy.draw(surface, font_small)
        self.btn_new_medium.draw(surface, font_small)
        self.btn_new_hard.draw(surface, font_small)
        self.btn_new_expert.draw(surface, font_small)
        self.btn_pencil.draw(surface, font_small)
        self.btn_undo.draw(surface, font_small)
        self.btn_hint.draw(surface, font_small)
        self.btn_auto_solve.draw(surface, font_small)
        self.btn_erase.draw(surface, font_small)
        for btn in self.numpad_btns:
            btn.draw(surface, font_small)
