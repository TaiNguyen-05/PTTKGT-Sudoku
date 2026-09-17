"""
Knuth's Algorithm X implemented with Dancing Links (DLX).
Transforms the 9x9 Sudoku problem into an Exact Cover problem with 729 rows and 324 columns.
Uses 4-way circular doubly linked lists for O(1) covering and uncovering operations.
"""
from typing import Generator, Tuple, List, Optional
import time
from core.board import Board
from algorithms.base_solver import BaseSolver, SolveMetrics


class DLXNode:
    def __init__(self, col_node: Optional["ColumnNode"] = None, row_info: Optional[Tuple[int, int, int]] = None):
        self.left: "DLXNode" = self
        self.right: "DLXNode" = self
        self.up: "DLXNode" = self
        self.down: "DLXNode" = self
        self.column: Optional["ColumnNode"] = col_node
        self.row_info: Optional[Tuple[int, int, int]] = row_info  # (row, col, value)


class ColumnNode(DLXNode):
    def __init__(self, name: str):
        super().__init__(self)
        self.size: int = 0
        self.name: str = name


class DancingLinksSolver(BaseSolver):
    def __init__(self):
        super().__init__("Dancing Links (Knuth's DLX / Algorithm X)")
        self.root: ColumnNode = ColumnNode("root")
        self.columns: List[ColumnNode] = []

    def _build_exact_cover_matrix(self, board: Board):
        """
        Khởi tạo ma trận Exact Cover với 324 cột và các hàng tương ứng với các quyết định (r, c, v).
        324 ràng buộc:
        1. 0..80: Mỗi ô (r, c) có đúng 1 số
        2. 81..161: Mỗi hàng r có đúng 1 số v
        3. 162..242: Mỗi cột c có đúng 1 số v
        4. 243..323: Mỗi khối b có đúng 1 số v
        """
        self.root = ColumnNode("root")
        self.columns = []

        # Tạo 324 cột
        prev = self.root
        for i in range(324):
            c_node = ColumnNode(f"C{i}")
            c_node.left = prev
            c_node.right = self.root
            prev.right = c_node
            self.root.left = c_node
            self.columns.append(c_node)
            prev = c_node

        # Tạo các hàng tương ứng với các khả năng điền
        for r in range(9):
            for c in range(9):
                val = board.get(r, c)
                box = (r // 3) * 3 + (c // 3)
                
                # Nếu ô đã có số cố định
                if val != 0:
                    candidates = [val]
                else:
                    candidates = list(range(1, 10))

                for v in candidates:
                    row_info = (r, c, v)
                    col_indices = [
                        r * 9 + c,                          # Ô (r, c)
                        81 + r * 9 + (v - 1),               # Hàng r có số v
                        162 + c * 9 + (v - 1),              # Cột c có số v
                        243 + box * 9 + (v - 1)             # Khối box có số v
                    ]

                    # Chèn 4 node liên kết ngang cho hàng này
                    first_node: Optional[DLXNode] = None
                    for col_idx in col_indices:
                        col = self.columns[col_idx]
                        node = DLXNode(col, row_info)

                        # Nối dọc vào cột
                        node.down = col
                        node.up = col.up
                        col.up.down = node
                        col.up = node
                        col.size += 1

                        # Nối ngang giữa 4 node cùng hàng
                        if first_node is None:
                            first_node = node
                        else:
                            node.left = first_node.left
                            node.right = first_node
                            first_node.left.right = node
                            first_node.left = node

    def _cover(self, col: ColumnNode) -> None:
        """Gỡ bỏ một cột và tất cả các hàng giao với cột đó khỏi ma trận."""
        col.right.left = col.left
        col.left.right = col.right

        row = col.down
        while row != col:
            j = row.right
            while j != row:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            row = row.down

    def _uncover(self, col: ColumnNode) -> None:
        """Khôi phục lại một cột và tất cả các hàng của nó theo thứ tự ngược lại."""
        row = col.up
        while row != col:
            j = row.left
            while j != row:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            row = row.up

        col.right.left = col
        col.left.right = col

    def _select_min_column(self) -> Optional[ColumnNode]:
        """Chọn cột có ít node nhất (Heuristic S của Knuth - tương đương MRV)."""
        min_size = float('inf')
        selected_col = None
        col = self.root.right
        while col != self.root:
            if col.size < min_size:
                min_size = col.size
                selected_col = col
                if min_size == 0:
                    break
            col = col.right
        return selected_col

    def solve(self, board: Board) -> Tuple[bool, SolveMetrics]:
        self.reset_metrics()
        start_time = time.perf_counter()

        self._build_exact_cover_matrix(board)
        solution: List[Tuple[int, int, int]] = []
        success = self._search_fast(solution)

        if success:
            for r, c, v in solution:
                board.set(r, c, v)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = SolveMetrics(
            algorithm_name=self.name,
            execution_time_ms=elapsed_ms,
            assignments=self.assignments,
            backtracks=self.backtracks,
            nodes_visited=self.nodes_visited,
            success=success
        )
        return success, metrics

    def _search_fast(self, solution: List[Tuple[int, int, int]]) -> bool:
        self.nodes_visited += 1

        if self.root.right == self.root:
            return True  # Tất cả các ràng buộc đã được phủ chính xác!

        col = self._select_min_column()
        if col is None or col.size == 0:
            return False  # Cột rỗng, không thể thỏa mãn ràng buộc này

        self._cover(col)

        row = col.down
        while row != col:
            solution.append(row.row_info)
            self.assignments += 1

            # Che các cột khác của hàng này
            j = row.right
            while j != row:
                self._cover(j.column)
                j = j.right

            if self._search_fast(solution):
                return True

            # Quay lui
            solution.pop()
            self.backtracks += 1

            j = row.left
            while j != row:
                self._uncover(j.column)
                j = j.left

            row = row.down

        self._uncover(col)
        return False

    def solve_stepwise(self, board: Board) -> Generator[Tuple[int, int, int, str], None, bool]:
        self.reset_metrics()
        self._build_exact_cover_matrix(board)
        solution: List[Tuple[int, int, int]] = []

        success = yield from self._search_generator(board, solution)
        return success

    def _search_generator(self, board: Board, solution: List[Tuple[int, int, int]]) -> Generator[Tuple[int, int, int, str], None, bool]:
        self.nodes_visited += 1

        if self.root.right == self.root:
            return True

        col = self._select_min_column()
        if col is None or col.size == 0:
            return False

        self._cover(col)

        row = col.down
        while row != col:
            r, c, v = row.row_info
            solution.append(row.row_info)
            self.assignments += 1

            # Chỉ animate các ô không phải ô cố định ban đầu
            if not board.is_fixed(r, c):
                board.set(r, c, v)
                yield (r, c, v, "TRY")

            j = row.right
            while j != row:
                self._cover(j.column)
                j = j.right

            res = yield from self._search_generator(board, solution)
            if res:
                if not board.is_fixed(r, c):
                    yield (r, c, v, "CONFIRM")
                return True

            solution.pop()
            self.backtracks += 1
            if not board.is_fixed(r, c):
                board.clear(r, c)
                yield (r, c, 0, "BACKTRACK")

            j = row.left
            while j != row:
                self._uncover(j.column)
                j = j.left

            row = row.down

        self._uncover(col)
        return False
