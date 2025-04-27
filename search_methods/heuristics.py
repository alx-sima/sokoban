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
    "boxes_minimum_moves_combination",
    "player_and_boxes_minimum_moves_combination",
    "distance_to_target_reachable",
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


def distance_to_target_reachable(state: Map) -> int:
    """
    Calculate the minimum number of pushes needed to move all boxes to a 
    corresponding target. A push is valid only if the player can reach the cell 
    opposite to the target.
    """
    reach = compute_reachable_positions(state)
    box_target_dist = np.zeros((len(state.boxes), len(state.targets)))

    for i, box in enumerate(state.boxes.values()):
        reach[box.x][box.y] = True
        distances = compute_distance_reachable_pushes(state, (box.x, box.y), reach)
        reach[box.x][box.y] = False

        for j, target in enumerate(state.targets):
            box_target_dist[i, j] = distances[target[0]][target[1]]

    rows, cols = optimize.linear_sum_assignment(box_target_dist)
    match = box_target_dist[rows, cols]
    return match.sum()
