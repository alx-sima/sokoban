from time import time

import numpy as np
from search_methods.solver import Solver
from search_methods.solution import Solution
from sokoban.map import Map

__all__ = ["BeamSearch"]


class BeamSearch(Solver):
    """
    Solver for Sokoban puzzle using the Beam Search algorithm.
    Attributes:
        - heuristic: A function for estimating the cost to reach the goal.
        - state_generator: A function that generates possible next states.
        - max_iters: Maximum number of iterations to run the algorithm
        (default: 100).
        - k: The number of states to keep in the beam (default: 20).
    """

    def __init__(self, base: Solver, k: int = 20) -> None:
        super().__init__(base.heuristic, base.state_generator, base.max_iters)
        self.k = k

    def solve(self, initial_state: Map) -> Solution:
        """
        Solve the Puzzle.
        Args:
            initial_state: The initial state of the puzzle.
        """
        state = initial_state.copy()
        beam = [([], state)]  # [(steps made, state)]

        self._start_time = time()
        explored_states = 0

        for _ in range(self.max_iters):
            beam_children = {}

            for idx, child in enumerate(beam):
                steps, state = child
                steps.append(str(state))

                # Solution found
                if state.is_solved():
                    explored_states += idx
                    return self._make_solution(
                        steps, explored_states, state.undo_moves
                    )

                children = self.state_generator(state)
                for child in children:
                    beam_children[str(child)] = (steps.copy(), child)

            candidates = list(beam_children.values())
            costs = np.fromiter(map(lambda x: self.heuristic(x[1]), candidates), int)
            costs = np.exp(costs.max() - costs)
            costs /= costs.sum()

            xs = np.random.choice(
                range(len(costs)), min(self.k, len(costs)), replace=False, p=costs
            )

            explored_states += len(beam)
            beam = [candidates[i] for i in xs]

        # No solution found in the given iterations
        return self._make_solution(steps, explored_states, state.undo_moves)

    def _make_solution(self, steps: list[str], explored_states: int, pull_moves: int):
        duration = time() - self._start_time
        return Solution(steps, explored_states, duration, pull_moves)
