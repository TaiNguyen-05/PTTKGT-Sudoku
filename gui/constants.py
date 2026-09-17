"""
Color tokens, layout metrics, and styling configurations for the Pygame UI.
Uses a curated Nord / Catppuccin Mocha aesthetic for a sleek, modern dark mode.
"""
import pygame

# Kích thước cửa sổ
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 740
FPS = 60

# Bảng màu thẩm mỹ cao (Curated Dark Palette)
COLOR_BG = (30, 30, 46)             # #1e1e2e - Nền ứng dụng chính
COLOR_SURFACE = (37, 37, 56)        # #252538 - Panel/Card nổi
COLOR_SURFACE_LIGHT = (49, 50, 68)  # #313244 - Viền hoặc nút phụ
COLOR_BORDER = (69, 71, 90)         # #45475a - Đường viền

# Màu chữ
COLOR_TEXT_PRIMARY = (205, 214, 244)   # #cdd6f4 - Chữ chính sáng rõ
COLOR_TEXT_MUTED = (166, 173, 200)     # #a6adc8 - Chữ phụ/chú thích
COLOR_TEXT_ACCENT = (137, 180, 250)    # #89b4fa - Chữ điểm nhấn xanh pastel

# Màu bàn cờ Sudoku
COLOR_BOARD_BG = (24, 24, 37)          # #181825 - Nền bàn cờ
COLOR_GRID_NORMAL = (69, 71, 90)       # Đường kẻ mảnh trong khối
COLOR_GRID_BOX = (137, 180, 250)       # Đường kẻ đậm giữa các khối 3x3
COLOR_CELL_SELECTED = (69, 71, 90)     # Ô đang được chọn
COLOR_CELL_SAME_VAL = (45, 52, 70)     # Các ô có cùng số với ô được chọn

# Trạng thái thuật toán (Visualizer colors)
COLOR_TRY = (249, 226, 175)            # #f9e2af - Vàng nhạt: Thuật toán đang gán thử số
COLOR_BACKTRACK = (243, 139, 168)      # #f38ba8 - Đỏ san hô: Đang quay lui
COLOR_CONFIRM = (166, 227, 161)        # #a6e3a1 - Xanh lá: Ô đã chốt chính xác
COLOR_CONFLICT = (235, 160, 172)       # Hồng đào: Ô vi phạm quy tắc

# Màu ô số
COLOR_NUM_FIXED = (245, 245, 250)      # Trắng sáng cho ô đề bài cố định
COLOR_NUM_USER = (137, 180, 250)       # Xanh dương cho người chơi điền
COLOR_NUM_PENCIL = (147, 153, 178)     # Xám cho số ghi chú bút chì

# Nút bấm (Buttons)
COLOR_BTN_PRIMARY = (137, 180, 250)    # Xanh dương chính
COLOR_BTN_PRIMARY_HOVER = (180, 190, 254)
COLOR_BTN_SECONDARY = (49, 50, 68)     # Nút xám tối
COLOR_BTN_SECONDARY_HOVER = (69, 71, 90)
COLOR_BTN_SUCCESS = (166, 227, 161)    # Xanh lá
COLOR_BTN_DANGER = (243, 139, 168)     # Đỏ cảnh báo

# Vị trí & Kích thước bàn cờ
BOARD_SIZE = 540                       # 540x540 pixels (mỗi ô 60x60)
CELL_SIZE = BOARD_SIZE // 9            # 60 pixels
BOARD_X = 50
BOARD_Y = 110
