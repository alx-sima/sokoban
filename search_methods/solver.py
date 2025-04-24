from typing import Callable

from sokoban.map import Map

__all__ = ["Solver"]


class Solver:
    """
    Base class for Sokoban puzzle solvers. For instantiating multiple algorithms
    or multiple runs of the same algorithms more easily.
    """

    def __init__(
        self,
        heuristic: Callable[[Map], int],
        state_generator: Callable[[Map], list[Map]],
        max_iters: int = 100,
    ) -> None:
        self.heuristic = heuristic
        self.state_generator = state_generator
        self.max_iters = max_iters

    def solve(self):
        raise NotImplementedError
