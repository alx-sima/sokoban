from time import time
from random import choice, random

from search_methods.solver import Solver
from search_methods.solution import Solution
from sokoban.map import Map

__all__ = ["LRTAstar"]


class LRTAstar(Solver):
    """
    Solver for Sokoban puzzle using the LRTA* algorithm.
    Attributes:
        - heuristic: A function for estimating the cost to reach the goal.
        - state_generator: A function that generates possible next states.
        - max_iters: Maximum number of iterations to run the algorithm
        (default: 100).
        - backoff_steps: Initial number of steps taken back on a backoff
        (default: 10).
        - backoff_step_increment: How many more steps backoff each time
        (default: 10).
        - backoff_probability_factor: How much does the chance of not backing
        off when no better state is found decreases e.g. 0.5 means the
        chance halves (default: 1.0 - no backoff).
        - cost_plateau_treshold: Number of steps without improvement before 
        trying to backoff (default: 20).
        - cost_estimations: A dictionary to store the cost estimations for
        states.
    """

    def __init__(
        self,
        base: Solver,
        max_iters: int = 100,
        backoff_steps: int = 10,
        backoff_step_increment: int = 10,
        backoff_probability_factor: float = 1.0,
        cost_plateau_treshold: int = 20,
    ) -> None:
        super().__init__(base.heuristic, base.state_generator, max_iters)
        self.backoff_steps = backoff_steps
        self.backoff_step_increment = backoff_step_increment
        self.backoff_probability_factor = backoff_probability_factor
        self.cost_plateau_treshold = cost_plateau_treshold

    def state_cost(self, state: Map):
        encoding = str(state)
        if encoding not in self.cost_estimations:
            self.cost_estimations[encoding] = self.heuristic(state)
        return self.cost_estimations[encoding]

    def solve(self, initial_state: Map) -> Solution:
        """
        Solve the puzzle.
        Args:
            initial_state: The initial state of the puzzle.
        """
        self.cost_estimations = {}
        self._start_time = time()
        self._extra_states_explored = 0
        self._backoffs = 0

        state = initial_state.copy()
        solution_steps = []

        min_cost_found = self.heuristic(state)
        backoff = self.backoff_steps
        chance_of_remaining = 1.0
        steps_no_improvement = 0

        for _ in range(self.max_iters):
            solution_steps.append(state)

            # Solution found
            if state.is_solved():
                return self._make_solution(
                    solution_steps, state.explored_states, state.undo_moves
                )

            neighbours = self.state_generator(state)
            costs = [1 + self.state_cost(n) for n in neighbours]
            min_cost = min(costs)

            minimal_states = [
                state for (cost, state) in zip(costs, neighbours) if cost == min_cost
            ]

            next_state = choice(minimal_states)
            self.cost_estimations[str(next_state)] = min_cost

            if min_cost >= min_cost_found:
                steps_no_improvement += 1

                if steps_no_improvement > self.cost_plateau_treshold:
                    # Backoff
                    if random() > chance_of_remaining:
                        steps_back = min(backoff, len(solution_steps))
                        self._extra_states_explored += steps_back
                        solution_steps = solution_steps[:-steps_back]
                        
                        backoff += self.backoff_step_increment
                        self._backoffs += 1

                        if len(solution_steps) == 0:
                            backoff = self.backoff_steps
                            state = initial_state.copy()
                        else:
                            state = solution_steps.pop()

                        min_cost_found = self.heuristic(state)
                        chance_of_remaining = 1.0
                        steps_no_improvement = 0
                        continue

                    else:
                        chance_of_remaining *= self.backoff_probability_factor
            else:
                min_cost_found = min_cost
                chance_of_remaining = 1.0
                steps_no_improvement = 0

            state = next_state

        # No solution found in the given iterations
        return self._make_solution(
            solution_steps, state.explored_states, state.undo_moves
        )

    def _make_solution(
        self, steps: list[Map], current_explored_states: int, pull_moves: int
    ) -> Solution:
        duration = time() - self._start_time
        explored_states = self._extra_states_explored + current_explored_states

        return self.LRTAstarSolution(
            [str(state) for state in steps],
            explored_states,
            duration,
            pull_moves,
            self._backoffs,
        )

    class LRTAstarSolution(Solution):
        """
        Stats about a solution found by LRTA*.
        Additional attributes:
            - backoffs: The number of backoffs performed during the search.
        """

        def __init__(
            self,
            steps: list[str],
            explored_states: int,
            time: float,
            undo_moves: int,
            backoffs: int,
        ):
            super().__init__(steps, explored_states, time, undo_moves)
            self.backoffs = backoffs

        def __str__(self) -> str:
            return super().__str__() + f", backoffs: {self.backoffs}"
