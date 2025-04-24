from scipy.optimize import linear_sum_assignment

import numpy as np

from sokoban.map import BOX_SYMBOL, OBSTACLE_SYMBOL, Map
from search_methods.utils import (
    compute_distance_matrix,
    compute_distance_reachable_pushes,
    compute_reachable_positions,
    in_bounds,
)

__all__ = ["boxes_placed", "boxes_total_distance_old", "boxes_total_distance"]


def boxes_placed(state: Map) -> int:
    cost = 0

    for target in state.targets:
        if target not in state.positions_of_boxes:
            cost += 1

    return cost


def boxes_total_distance_old(state: Map) -> int:
    free_targets = []
    boxes_on_target = set()

    for target in state.targets:
        if target not in state.positions_of_boxes:
            free_targets.append(target)
            continue

        box_name = state.positions_of_boxes[target]
        boxes_on_target.add(box_name)

    if len(free_targets) == 0:
        return 0

    goal_distances = compute_distance_matrix(state, free_targets, [1])

    cost = 0
    if len(free_targets) > 1:
        for i in range(len(free_targets)):
            goal_distances2 = compute_distance_matrix(
                state, free_targets[:i] + free_targets[i + 1 :], [1]
            )
            target_distance = 0

            for box in state.boxes.values():
                if box.name in boxes_on_target:
                    continue

                target_distance = max(target_distance, goal_distances2[box.x][box.y])

            cost += target_distance

    for box in state.boxes.values():
        if box.name in boxes_on_target:
            continue

        target_distance = goal_distances[box.x][box.y]
        cost += target_distance

    return cost


def boxes_total_distance(state: Map) -> int:
    box_target_distances = np.zeros((len(state.boxes), len(state.targets)))

    for i, target in enumerate(state.targets):
        distances = compute_distance_matrix(state, [target], [OBSTACLE_SYMBOL])

        for j, box in enumerate(state.boxes.values()):
            box_target_distances[i, j] = distances[box.x][box.y]

    rows, cols = linear_sum_assignment(box_target_distances)
    match = box_target_distances[rows, cols]
    return match.sum()


def boxes_distance_and_reach_distance(state: Map) -> int:
    player_reach = compute_distance_matrix(
        state, [(state.player.x, state.player.y)], [OBSTACLE_SYMBOL],
        restrict_pushes=False,
    )
    

    # min_box_distance = min(map(lambda b: player_reach[b.x][b.y], state.boxes.values()))
    min_box_distance = 0
    # min_box_distance = max(map(lambda b: (state.player.x - b.x) + abs(state.player.y - b.y), state.boxes.values()))
    return min_box_distance + boxes_total_distance(state)


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
        print('====')
        for j, target in enumerate(state.targets):
            box_target_dist[i, j] = distances[target[0]][target[1]]

    rows, cols = linear_sum_assignment(box_target_dist)
    match = box_target_dist[rows, cols]
    print(match)
    breakpoint()
    return match.sum()
