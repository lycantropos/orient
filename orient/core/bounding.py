from typing import (Iterable,
                    Tuple)

from orient.hints import (Coordinate,
                          Point)
from .utils import flatten

Box = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]


def box_contains_point(box: Box, point: Point) -> bool:
    x_min, x_max, y_min, y_max = box
    point_x, point_y = point
    return x_min <= point_x <= x_max and y_min <= point_y <= y_max


def box_disjoint_with(goal: Box, test: Box) -> bool:
    ((goal_x_min, goal_x_max, goal_y_min, goal_y_max),
     (test_x_min, test_x_max, test_y_min, test_y_max)) = goal, test
    return (goal_x_max < test_x_min or test_x_max < goal_x_min
            or goal_y_max < test_y_min or test_y_max < goal_y_min)


def box_from_iterable(points: Iterable[Point]) -> Box:
    iterator = iter(points)
    x_min, y_min = x_max, y_max = next(iterator)
    for x, y in iterator:
        x_min, x_max, y_min, y_max = (min(x_min, x), max(x_max, x),
                                      min(y_min, y), max(y_max, y))
    return x_min, x_max, y_min, y_max


def box_from_iterables(iterables: Iterable[Iterable[Point]]) -> Box:
    return box_from_iterable(flatten(iterables))
