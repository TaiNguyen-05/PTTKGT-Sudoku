"""
Unit tests for all 4 Sudoku solving algorithms and the Board data structure.
"""
import pytest
from core.board import Board
from core.dataset import get_sample_puzzle, AI_ESCARGOT
from core.generator import generate_sudoku
from algorithms.naive_backtracking import NaiveBacktrackingSolver
from algorithms.heuristic_backtracking import HeuristicBacktrackingSolver
from algorithms.dancing_links import DancingLinksSolver
from algorithms.simulated_annealing import SimulatedAnnealingSolver


TEST_PUZZLE = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"


def test_board_initialization():
    board = Board.from_string(TEST_PUZZLE)
    assert board.get(0, 2) == 3
    assert board.is_fixed(0, 2) is True
    assert board.get(0, 0) == 0
    assert board.is_fixed(0, 0) is False
    assert board.count_empty_cells() > 0


def test_naive_backtracking():
    board = Board.from_string(TEST_PUZZLE)
    solver = NaiveBacktrackingSolver()
    success, metrics = solver.solve(board)
    assert success is True
    assert board.is_solved() is True
    assert metrics.assignments > 0
    assert metrics.execution_time_ms >= 0


def test_heuristic_backtracking():
    board = Board.from_string(TEST_PUZZLE)
    solver = HeuristicBacktrackingSolver()
    success, metrics = solver.solve(board)
    assert success is True
    assert board.is_solved() is True
    assert metrics.nodes_visited > 0


def test_dancing_links():
    board = Board.from_string(TEST_PUZZLE)
    solver = DancingLinksSolver()
    success, metrics = solver.solve(board)
    assert success is True
    assert board.is_solved() is True
    assert metrics.assignments > 0


def test_dancing_links_ai_escargot():
    """Test DLX on the legendary AI Escargot."""
    board = Board.from_string(AI_ESCARGOT)
    solver = DancingLinksSolver()
    success, metrics = solver.solve(board)
    assert success is True
    assert board.is_solved() is True


def test_heuristic_ai_escargot():
    """Test MRV CSP on AI Escargot."""
    board = Board.from_string(AI_ESCARGOT)
    solver = HeuristicBacktrackingSolver()
    success, metrics = solver.solve(board)
    assert success is True
    assert board.is_solved() is True


def test_generator():
    board = generate_sudoku("Easy")
    assert board.count_empty_cells() >= 35
    solver = DancingLinksSolver()
    success, _ = solver.solve(board)
    assert success is True
    assert board.is_solved() is True
