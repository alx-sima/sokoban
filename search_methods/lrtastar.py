from time import time
from typing import Callable
from random import choice

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
        - max_restarts: Maximum number of restarts to perform  (default: 20).
        - steps_before_restart: Number of steps until, if a state with a better
        cost is not found, the algorithm will restart (default: 20). 'None'
        disables restarting.
        - cost_estimations: A dictionary to store the cost estimations for
        states.
        - enhancement_retries: Number of times to retry the search for a
        better solution after the first one is found (default: 0).
    """

    def __init__(
        self,
        base: Solver,
        max_restarts: int = 20,
        steps_before_restart: int | None = 20,
        enhancement_retries: int = 0,
    ) -> None:
        super().__init__(base.heuristic, base.state_generator, base.max_iters)
        self.max_restarts = max_restarts
        self.steps_before_restart = steps_before_restart
        self.enhancement_retries = enhancement_retries

    def state_cost(self, state: Map):
        encoding = str(state)
        if encoding not in self.cost_estimations:
            self.cost_estimations[encoding] = self.heuristic(state)
        return self.cost_estimations[encoding]

    def solve(self, initial_state: Map) -> Solution:
        """
        Solve the puzzle. Clear all memory before solving.
        Args:
            initial_state: The initial state of the puzzle.
        """
        self.cost_estimations = {}
        self._start_time = time()
        self._restarts = 0
        self._previous_explored_states = 0

        solution = self._solve(initial_state)
        if not solution.is_solved():
            return solution  # Nothing to enhance

        print(len(solution.steps))

        for _ in range(self.enhancement_retries):
            new_solution = self._solve(initial_state)
            if (
                len(new_solution.steps) < len(solution.steps)
                and new_solution.is_solved()
            ):
                solution = new_solution
                print(len(solution.steps))

        return solution

    def _solve(self, initial_state: Map) -> Solution:
        state = initial_state.copy()
        solution_steps = []

        min_cost_found = self.heuristic(state)
        steps_no_improvement = 0

        for _ in range(self.max_iters):
            state_encoding = str(state)
            solution_steps.append(state_encoding)

            # Solution found
            if state.is_solved():
                return self._make_solution(
                    solution_steps, state.explored_states, state.undo_moves
                )

            neighbours = self.state_generator(state)
            costs = [1 + self.state_cost(n) for n in neighbours]
            min_cost = min(costs)

            # TODO: refactor
            next_states = list(
                filter(lambda x: x[0] == min_cost, zip(costs, neighbours))
            )
            _, next_state = choice(next_states)

            if min_cost >= min_cost_found:
                steps_no_improvement += 1
                if (
                    self.steps_before_restart is not None
                    and steps_no_improvement >= self.steps_before_restart
                ):
                    return self._restart_search(solution_steps, state, initial_state)
            else:
                min_cost_found = min_cost
                steps_no_improvement = 0

            self.cost_estimations[str(next_state)] = min_cost
            state = next_state

        # No solution found in the given iterations, restart searching
        return self._restart_search(solution_steps, state, initial_state)

    def _restart_search(
        self, solution_steps: list[str], current_state: Map, initial_state: Map
    ) -> Solution:
        self._restarts += 1
        if self._restarts >= self.max_restarts:
            return self._make_solution(
                solution_steps, current_state.explored_states, current_state.undo_moves
            )

        self._previous_explored_states += current_state.explored_states
        return self._solve(initial_state)

    def _make_solution(
        self, steps: list[str], current_explored_states: int, pull_moves: int
    ) -> Solution:
        duration = time() - self._start_time
        explored_states = self._previous_explored_states + current_explored_states

        return self.LRTAstarSolution(
            steps, explored_states, duration, pull_moves, self._restarts
        )

    class LRTAstarSolution(Solution):
        """
        Stats about a solution found by LRTA*.
        Additional attributes:
            - restarts: The number of restarts performed during the search.
        """

        def __init__(
            self,
            steps: list[str],
            explored_states: int,
            time: float,
            undo_moves: int,
            restarts: int,
        ):
            super().__init__(steps, explored_states, time, undo_moves)
            self.restarts = restarts

        def __str__(self) -> str:
            return super().__str__() + f", restarts: {self.restarts}"
