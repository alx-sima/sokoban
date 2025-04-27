from sokoban import Map
from queue import Queue

from sokoban.map import BOX_SYMBOL, OBSTACLE_SYMBOL

__all__ = [
    "get_neighbours",
    "get_neighbours_no_pulls",
    "in_bounds",
    "manhattan_distance",
    "compute_distance_matrix",
    "compute_reachable_positions",
    "compute_distance_reachable_pushes",
]

# Cost of an unreachable position
WALL_COST = 100


def get_neighbours(state: Map) -> list[Map]:
    """Get all neighbours of a state."""
    return state.get_neighbours()


def get_neighbours_no_pulls(state: Map) -> list[Map]:
    """Get all neighbours of a state, but only those that are not pull moves."""
    return [n for n in state.get_neighbours() if n.undo_moves == 0]


def in_bounds(state: Map, x: int, y: int) -> bool:
    """Check if a position is within the bounds of the map."""
    return x >= 0 and y >= 0 and x < state.length and y < state.width


def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Calculate the manhattan distance between two points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def compute_distance_matrix(
    state: Map,
    starts: list[tuple[int, int]],
    invalid_values: list[int],
    restrict_pushes: bool = True,
) -> list[list[int]]:
    """
    Compute the distance matrix from a list of starting points to all others.
    Args:
        state: The map.
        starts: The starting points.
        invalid_values: The values that are considered invalid (e.g. walls,
        other boxes).
        restrict_pushes: If True, calculate the distance in pushes, not moves.
    """
    distances = [[WALL_COST for _ in range(state.width)] for _ in range(state.length)]
    q = Queue()
    for x, y in starts:
        distances[x][y] = 0
        q.put((x, y))

    while not q.empty():
        x, y = q.get()

        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in offsets:
            x2, y2 = x + dx, y + dy
            if not in_bounds(state, x2, y2) or state.map[x2][y2] in invalid_values:
                continue

            if restrict_pushes:
                x3, y3 = x2 + dx, y2 + dy
                if not in_bounds(state, x3, y3) or state.map[x3][y3] in invalid_values:
                    continue

            if distances[x2][y2] > distances[x][y] + 1:
                distances[x2][y2] = distances[x][y] + 1
                q.put((x2, y2))

    return distances


def compute_reachable_positions(state: Map) -> list[list[bool]]:
    """Compute the reachable positions from the player position."""
    reach = [[False for _ in range(state.width)] for _ in range(state.length)]
    q = Queue()

    reach[state.player.x][state.player.y] = True
    q.put((state.player.x, state.player.y))

    while not q.empty():
        x, y = q.get()

        offsets = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for nx, ny in offsets:
            if not in_bounds(state, nx, ny) or state.map[nx][ny] in [
                OBSTACLE_SYMBOL,
                BOX_SYMBOL,
            ]:
                continue

            if not reach[nx][ny]:
                reach[nx][ny] = True
                q.put((nx, ny))

    return reach


def compute_distance_reachable_pushes(
    state: Map, box: tuple[int, int], reach: list[list[bool]]
) -> int:
    """
    Compute the distance from a box to all other cells, with pushes made only
    from player-reachable positions.
    """
    distances = [[WALL_COST for _ in range(state.width)] for _ in range(state.length)]
    q = Queue()
    distances[box[0]][box[1]] = 0
    q.put((box[0], box[1]))

    while not q.empty():
        x, y = q.get()

        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in offsets:
            px, py = x - dx, y - dy
            tx, ty = x + dx, y + dy

            if not in_bounds(state, px, py) or not in_bounds(state, tx, ty):
                continue
            if state.map[tx][ty] == OBSTACLE_SYMBOL or not reach[px][py]:
                continue

            cost = distances[x][y] + 1
            if distances[tx][ty] > cost:
                distances[tx][ty] = cost
                q.put((tx, ty))

    return distances
