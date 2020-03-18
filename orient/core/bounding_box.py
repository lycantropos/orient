from typing import (Iterable,
                    Tuple)

from orient.hints import (Coordinate,
                          Point)

BoundingBox = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]


def contains_bounding_box(goal: BoundingBox, test: BoundingBox) -> bool:
    ((goal_x_min, goal_x_max, goal_y_min, goal_y_max),
     (test_x_min, test_x_max, test_y_min, test_y_max)) = goal, test
    return (goal_x_min <= test_x_min and test_x_max <= goal_x_max
            and goal_y_min <= test_y_min and test_y_max <= goal_y_max)


def from_points(points: Iterable[Point]) -> BoundingBox:
    iterator = iter(points)
    x_min, y_min = x_max, y_max = next(iterator)
    for x, y in iterator:
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max
