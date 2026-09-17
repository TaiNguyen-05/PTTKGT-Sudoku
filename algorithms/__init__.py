from algorithms.base_solver import BaseSolver, SolveMetrics
from algorithms.naive_backtracking import NaiveBacktrackingSolver
from algorithms.heuristic_backtracking import HeuristicBacktrackingSolver
from algorithms.dancing_links import DancingLinksSolver
from algorithms.simulated_annealing import SimulatedAnnealingSolver

SOLVER_MAP = {
    "Naive Backtracking": NaiveBacktrackingSolver,
    "Heuristic CSP (MRV+LCV)": HeuristicBacktrackingSolver,
    "Dancing Links (DLX)": DancingLinksSolver,
    "Simulated Annealing": SimulatedAnnealingSolver,
}

__all__ = [
    "BaseSolver",
    "SolveMetrics",
    "NaiveBacktrackingSolver",
    "HeuristicBacktrackingSolver",
    "DancingLinksSolver",
    "SimulatedAnnealingSolver",
    "SOLVER_MAP"
]
