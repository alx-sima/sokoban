from shutil import rmtree
from tempfile import mkdtemp
from sokoban.gif import create_gif, save_images
from sokoban.map import Map

__all__ = ["Solution"]


class Solution:
    """
    Class to store the solution (and different info about how it was obtained)
    for a Sokoban puzzle.
    Attributes:
        - steps: The succession of states (as strings) of the game towards the
        solution.
        - length: The number of steps in the solution.
        - expanded_states: The number of states explored during the search.
        - time: The time taken to find the solution.
        - pull_moves: The number of box pulls made.
    """

    def __init__(
        self,
        steps: list[str],
        expanded_states: int,
        time: float,
        pull_moves: int,
    ):
        self.steps = steps
        self.length = len(steps)
        self.expanded_states = expanded_states
        self.time = time
        self.pull_moves = pull_moves

    def __str__(self) -> str:
        return (
            f"steps: {self.length}"
            + f", solved: {self.is_solved()}"
            + f", explored states: {self.expanded_states}"
            + f", time: {self.time:.2f}s"
            + f", pull moves: {self.pull_moves}"
        )

    def is_solved(self) -> bool:
        """Check if the solution found actually solves the puzzle."""
        if len(self.steps) == 0:
            return False

        return Map.from_str(self.steps[-1]).is_solved()

    def save(self, name: str, path: str = ".") -> None:
        """Save the solution as a gif."""
        tmpdir = mkdtemp()
        save_images(self.steps, tmpdir)
        create_gif(tmpdir, name, path)
        rmtree(tmpdir)

    @staticmethod
    def average(solutions: list["Solution"]) -> "Solution":
        """
        Calculate the average statistics of solutions.
        """
        if len(solutions) == 0:
            return Solution([], 0, 0, 0)

        expanded_states = sum(s.expanded_states for s in solutions) / len(solutions)
        time = sum(s.time for s in solutions) / len(solutions)
        pull_moves = sum(s.pull_moves for s in solutions) / len(solutions)

        avg_sol = Solution([], expanded_states, time, pull_moves)
        avg_sol.length = sum(s.length for s in solutions) / len(solutions)

        return avg_sol
