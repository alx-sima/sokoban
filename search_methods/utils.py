from shutil import rmtree
from tempfile import mkdtemp
from sokoban import Map
from queue import Queue

from sokoban.map import BOX_SYMBOL, OBSTACLE_SYMBOL
from sokoban.gif import create_gif, save_images

__all__ = [
    "constant_cost",
    "penalize_pulls",
    "get_neighbours",
    "get_neighbours_no_pulls",
    "save_play",
    "in_bounds",
    "dist",
    "compute_distance_matrix",
    "compute_reachable_positions",
]

WALL_COST = 100


def get_neighbours(state: Map) -> list[Map]:
    return state.get_neighbours()


def get_neighbours_no_pulls(state: Map) -> list[Map]:
    return [n for n in state.get_neighbours() if n.undo_moves == 0]


def in_bounds(state: Map, x: int, y: int) -> bool:
    return x >= 0 and y >= 0 and x < state.length and y < state.width


def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def compute_distance_matrix(
    state: Map,
    starts: list[tuple[int, int]],
    invalid_values: list[int],
    restrict_pushes: bool = True,
) -> list[list[int]]:
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


# def compute_reachable_positions(state: Map) -> list[list[int]]:
#     PUSH_COST = 20
#     reach = [[WALL_COST for _ in range(state.width)] for _ in range(state.length)]
#     q = Queue()
#     reach[state.player.x][state.player.y] = 0
#     q.put((state.player.x, state.player.y))

#     while not q.empty():
#         x, y = q.get()

#         offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
#         for dx, dy in offsets:
#             tx, ty = x + dx, y + dy
#             if not in_bounds(state, tx, ty) or state.map[tx][ty] == OBSTACLE_SYMBOL:
#                 continue

#             parent_cost = reach[x][y]
#             if state.map[x][y] == BOX_SYMBOL:
#                 parent_cost += PUSH_COST

#             if reach[tx][ty] > parent_cost:
#                 reach[tx][ty] = parent_cost
#                 q.put((tx, ty))

#     return reach


def compute_distance_reachable_pushes(
    state: Map, box: tuple[int, int], reach: list[list[bool]]
) -> int:
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


def compute_distance_reachable_pushes2(
    state: Map, box: tuple[int, int], reach: list[list[bool]]
) -> list[list[int]]:
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
            if state.map[tx][ty] == OBSTACLE_SYMBOL:
                continue

            if not reach[px][py]:
                continue

            if distances[tx][ty] > distances[x][y] + 1:
                distances[tx][ty] = distances[px][py] + 1
                q.put((tx, ty))

    return distances


def find_player_position(
    state: Map, distance: list[list[int]], target: tuple[int, int]
) -> list[tuple[int, int]]:
    x, y = target
    possible_positions = []

    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dx, dy in offsets:
        px, py = x + dx, y + dy
        if not in_bounds(state, px, py):
            continue

        if distance[x][y] == distance[px][py] + 1:
            possible_positions.append((px, py))


def compute_reachable_positions(state: Map) -> list[list[bool]]:
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


def save_play(moves: list[Map | str], name: str, path: str = "."):
    tmpdir = mkdtemp()
    save_images(moves, tmpdir)
    create_gif(tmpdir, name, path)
    rmtree(tmpdir)
