"""
Board representation and validation logic for Sudoku (9x9).
Supports bitmasking for fast constraint validation and candidate queries.
"""
from typing import List, Tuple, Set, Optional
import copy


class Board:
    """
    Biểu diễn bàn cờ Sudoku 9x9.
    0 đại diện cho ô trống.
    """
    SIZE = 9
    BOX_SIZE = 3

    def __init__(self, grid: Optional[List[List[int]]] = None):
        if grid:
            self.grid = [row[:] for row in grid]
        else:
            self.grid = [[0 for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        
        # Đánh dấu các ô ban đầu (đề bài cố định - clues)
        self.initial_mask = [[(self.grid[r][c] != 0) for c in range(self.SIZE)] for r in range(self.SIZE)]

    @classmethod
    def from_string(cls, puzzle_str: str) -> "Board":
        """
        Khởi tạo Board từ chuỗi 81 ký tự.
        Các ký tự '.' hoặc '0' đại diện cho ô trống.
        """
        cleaned = "".join(c for c in puzzle_str.strip() if c.isdigit() or c == '.')
        if len(cleaned) < 81:
            raise ValueError(f"Chuỗi đề bài phải có ít nhất 81 ký tự, hiện tại: {len(cleaned)}")
        
        grid = []
        for r in range(9):
            row = []
            for c in range(9):
                char = cleaned[r * 9 + c]
                val = 0 if char in ('.', '0') else int(char)
                row.append(val)
            grid.append(row)
        return cls(grid)

    def to_string(self) -> str:
        """Xuất bàn cờ ra chuỗi 81 ký tự."""
        return "".join(str(self.grid[r][c]) for r in range(9) for c in range(9))

    def copy(self) -> "Board":
        """Tạo bản sao sâu của Board."""
        new_board = Board(self.grid)
        new_board.initial_mask = [row[:] for row in self.initial_mask]
        return new_board

    def is_fixed(self, row: int, col: int) -> bool:
        """Kiểm tra ô có phải là ô đề bài cố định hay không."""
        return self.initial_mask[row][col]

    def get(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def set(self, row: int, col: int, val: int) -> None:
        self.grid[row][col] = val

    def clear(self, row: int, col: int) -> None:
        self.grid[row][col] = 0

    def is_valid_placement(self, row: int, col: int, val: int) -> bool:
        # Kiểm tra hàng
        for c in range(self.SIZE):
            if c != col and self.grid[row][c] == val:
                return False

        # Kiểm tra cột
        for r in range(self.SIZE):
            if r != row and self.grid[r][col] == val:
                return False

        # Kiểm tra khối 3x3
        box_r = (row // self.BOX_SIZE) * self.BOX_SIZE
        box_c = (col // self.BOX_SIZE) * self.BOX_SIZE
        for r in range(box_r, box_r + self.BOX_SIZE):
            for c in range(box_c, box_c + self.BOX_SIZE):
                if (r != row or c != col) and self.grid[r][c] == val:
                    return False

        return True

    def get_candidates(self, row: int, col: int) -> Set[int]:
        if self.grid[row][col] != 0:
            return set()

        used = set()
        # Ràng buộc hàng & cột
        for i in range(self.SIZE):
            if self.grid[row][i] != 0:
                used.add(self.grid[row][i])
            if self.grid[i][col] != 0:
                used.add(self.grid[i][col])

        # Ràng buộc khối 3x3
        box_r = (row // self.BOX_SIZE) * self.BOX_SIZE
        box_c = (col // self.BOX_SIZE) * self.BOX_SIZE
        for r in range(box_r, box_r + self.BOX_SIZE):
            for c in range(box_c, box_c + self.BOX_SIZE):
                if self.grid[r][c] != 0:
                    used.add(self.grid[r][c])

        return set(range(1, 10)) - used

    def find_empty_cell(self) -> Optional[Tuple[int, int]]:
        """Tìm ô trống đầu tiên (theo thứ tự quét hàng-cột thông thường)."""
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] == 0:
                    return (r, c)
        return None

    def get_all_empty_cells(self) -> List[Tuple[int, int]]:
        """Lấy danh sách tất cả các ô trống."""
        return [(r, c) for r in range(self.SIZE) for c in range(self.SIZE) if self.grid[r][c] == 0]

    def count_empty_cells(self) -> int:
        return sum(1 for r in range(self.SIZE) for c in range(self.SIZE) if self.grid[r][c] == 0)

    def is_solved(self) -> bool:
        """Kiểm tra bàn cờ đã được giải hoàn tất và hợp lệ 100% chưa."""
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                val = self.grid[r][c]
                if val == 0 or not self.is_valid_placement(r, c, val):
                    return False
        return True

    def is_valid_board(self) -> bool:
        """Kiểm tra bàn cờ hiện tại có bị xung đột nào giữa các ô đã điền không."""
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                val = self.grid[r][c]
                if val != 0:
                    if not self.is_valid_placement(r, c, val):
                        return False
        return True

    def count_conflicts(self) -> int:
        """
        Tính số lượng xung đột trên toàn bàn cờ (dùng cho Simulated Annealing).
        Đếm số lần lặp lại số trên mỗi hàng và mỗi cột.
        """
        conflicts = 0
        # Xung đột hàng
        for r in range(self.SIZE):
            seen = set()
            for c in range(self.SIZE):
                v = self.grid[r][c]
                if v != 0:
                    if v in seen:
                        conflicts += 1
                    seen.add(v)

        # Xung đột cột
        for c in range(self.SIZE):
            seen = set()
            for r in range(self.SIZE):
                v = self.grid[r][c]
                if v != 0:
                    if v in seen:
                        conflicts += 1
                    seen.add(v)

        return conflicts

    def __repr__(self) -> str:
        lines = []
        for r in range(self.SIZE):
            if r % 3 == 0 and r != 0:
                lines.append("-" * 21)
            row_str = []
            for c in range(self.SIZE):
                if c % 3 == 0 and c != 0:
                    row_str.append("|")
                val = self.grid[r][c]
                row_str.append(str(val) if val != 0 else ".")
            lines.append(" ".join(row_str))
        return "\n".join(lines)
