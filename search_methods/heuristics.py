from scipy import optimize

from sokoban.map import OBSTACLE_SYMBOL, Map
from search_methods.utils import (
    compute_distance_matrix,
    compute_distance_reachable_pushes,
    compute_reachable_positions,
    manhattan_distance,
)

import numpy as np

__all__ = [
    "manhattan_min_distances",
    "boxes_total_distance_old",
    "boxes_minimum_moves_combination",
]


def manhattan_min_distances(state: Map) -> int:
    """
    Calculate the sum of the (manhattan) distances from each box to the closest
    target.
    """
    total_distances = 0

    for box in state.boxes.values():
        target_distances = map(
            lambda t: manhattan_distance((box.x, box.y), t), state.targets
        )
        total_distances += min(target_distances)

    return total_distances


def boxes_minimum_moves_combination(state: Map) -> int:
    """
    Calculates the minimum number of pushes needed to move all boxes to a
    corresponding target.
    """
    box_target_distances = np.zeros((len(state.boxes), len(state.targets)))

    for i, target in enumerate(state.targets):
        distances = compute_distance_matrix(state, [target], [OBSTACLE_SYMBOL])

        for j, box in enumerate(state.boxes.values()):
            try:
                box_target_distances[i, j] = distances[box.x][box.y]
            except IndexError:
                state.plot_map()
                print(len(state.boxes), len(state.targets))
                raise

    rows, cols = optimize.linear_sum_assignment(box_target_distances)
    match = box_target_distances[rows, cols]
    return match.sum()


def player_and_boxes_minimum_moves_combination(state: Map) -> int:
    """
    Calculates the steps to the closest box and the minimum number of pushes
    needed to move all boxes to a corresponding target (ignoring walls).
    """
    player_distances = compute_distance_matrix(
        state,
        [(state.player.x, state.player.y)],
        [OBSTACLE_SYMBOL],
        restrict_pushes=False,
    )

    box_distances = map(lambda b: player_distances[b.x][b.y], state.boxes.values())
    return min(box_distances) + boxes_minimum_moves_combination(state)


def boxes_distance_and_reach_distance(state: Map) -> int:
    player_reach = compute_distance_matrix(
        state,
        [(state.player.x, state.player.y)],
        [OBSTACLE_SYMBOL],
        restrict_pushes=False,
    )

    # min_box_distance = min(map(lambda b: player_reach[b.x][b.y], state.boxes.values()))
    min_box_distance = 0
    # min_box_distance = max(map(lambda b: (state.player.x - b.x) + abs(state.player.y - b.y), state.boxes.values()))
    return min_box_distance + boxes_minimum_moves_combination(state)


def distance_to_target_reachable(state: Map) -> int:
    reach = compute_reachable_positions(state)
    for i in reach[::-1]:
        print(i)
    box_target_dist = np.zeros((len(state.boxes), len(state.targets)))

    for i, box in enumerate(state.boxes.values()):
        reach[box.x][box.y] = True
        distances = compute_distance_reachable_pushes(state, (box.x, box.y), reach)
        reach[box.x][box.y] = False
        for t in distances[::-1]:
            print(t)
        print("====")
        for j, target in enumerate(state.targets):
            box_target_dist[i, j] = distances[target[0]][target[1]]

    rows, cols = optimize.linear_sum_assignment(box_target_dist)
    match = box_target_dist[rows, cols]
    print(match)
    breakpoint()
    return match.sum()
