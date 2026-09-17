"""
Procedural Sudoku Generator with Unique Solution Guarantee.
Uses backtracking with randomized candidate order to generate full boards,
then knocks out clues symmetrically while ensuring the puzzle has a unique solution.
"""
import random
from typing import Tuple, List, Optional
from core.board import Board


def count_solutions(board: Board, limit: int = 2) -> int:
    """
    Đếm số nghiệm của bàn cờ Sudoku (dừng sớm nếu đạt `limit`).
    Dùng phương pháp MRV (Minimum Remaining Values) nhanh để kiểm tra nghiệm duy nhất.
    """
    # Tìm ô có ít ứng viên nhất
    min_candidates = 10
    best_cell = None
    best_cands = set()

    for r in range(9):
        for c in range(9):
            if board.get(r, c) == 0:
                cands = board.get_candidates(r, c)
                if len(cands) == 0:
                    return 0 # Ngõ cụt, vô nghiệm
                if len(cands) < min_candidates:
                    min_candidates = len(cands)
                    best_cell = (r, c)
                    best_cands = cands
                    if min_candidates == 1:
                        break
        if min_candidates == 1:
            break

    # Nếu không còn ô trống nào -> Đã tìm thấy 1 nghiệm hợp lệ
    if best_cell is None:
        return 1

    r, c = best_cell
    total = 0
    for val in best_cands:
        board.set(r, c, val)
        total += count_solutions(board, limit - total)
        board.clear(r, c)
        if total >= limit:
            break

    return total


def fill_board_randomly(board: Board) -> bool:
    """
    Điền toàn bộ bàn cờ ngẫu nhiên để tạo một cấu hình Sudoku hoàn chỉnh hợp lệ.
    """
    empty = board.find_empty_cell()
    if empty is None:
        return True

    r, c = empty
    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for num in numbers:
        if board.is_valid_placement(r, c, num):
            board.set(r, c, num)
            if fill_board_randomly(board):
                return True
            board.clear(r, c)

    return False


def generate_sudoku(difficulty: str = "Medium") -> Board:
    """
    Sinh đề Sudoku mới đảm bảo nghiệm duy nhất theo cấp độ:
    - Easy: 36 - 40 clues
    - Medium: 30 - 34 clues
    - Hard: 26 - 29 clues
    - Expert: 22 - 25 clues
    """
    target_clues_map = {
        "Easy": random.randint(36, 40),
        "Medium": random.randint(30, 34),
        "Hard": random.randint(26, 29),
        "Expert": random.randint(22, 25),
    }
    target_clues = target_clues_map.get(difficulty, 32)

    # 1. Tạo bàn cờ đầy đủ ngẫu nhiên
    board = Board()
    fill_board_randomly(board)

    # 2. Xáo trộn danh sách vị trí để đào lỗ (knocking out cells)
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    current_clues = 81
    for r, c in positions:
        if current_clues <= target_clues:
            break

        backup = board.get(r, c)
        board.clear(r, c)

        # Kiểm tra xem bỏ ô này thì bài toán còn nghiệm duy nhất không
        if count_solutions(board, limit=2) != 1:
            # Nếu mất tính duy nhất của nghiệm, khôi phục lại
            board.set(r, c, backup)
        else:
            current_clues -= 1

    # Tạo đối tượng Board chuẩn với initial_mask được cập nhật đúng các clues
    result_board = Board(board.grid)
    return result_board
