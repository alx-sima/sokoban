from sokoban.map import Map

__all__ = ["Solution"]


class Solution:
    """
    Class to store the solution (and different info about how it was obtained)
    for a Sokoban puzzle.
    Attributes:
        - steps: A list of strings representing the solution path.
        - explored_states: The number of states explored during the search.
        - time: The time taken to find the solution.
        - pull_moves: The number of box pulls made.
    """

    def __init__(
        self,
        steps: list[str],
        explored_states: int,
        time: float,
        pull_moves: int,
    ):
        self.steps = steps
        self.explored_states = explored_states
        self.time = time
        self.pull_moves = pull_moves

    def __str__(self) -> str:
        return (
            f"steps: {len(self.steps)}"
            + f", solved: {self.is_solved()}"
            + f", explored states: {self.explored_states}"
            + f", time: {self.time:.2f}s"
            + f", pull moves: {self.pull_moves}"
        )

    def is_solved(self) -> bool:
        """Check if the solution found actually solves the puzzle."""
        if len(self.steps) == 0:
            return False

        return Map.from_str(self.steps[-1]).is_solved()
