from typing import (Iterable,
                    Tuple)

from orient.hints import (Coordinate,
                          Point)
from .utils import flatten

BoundingBox = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]


def contains_point(bounding_box: BoundingBox, point: Point) -> bool:
    x_min, x_max, y_min, y_max = bounding_box
    point_x, point_y = point
    return x_min <= point_x <= x_max and y_min <= point_y <= y_max


def disjoint_with(goal: BoundingBox, test: BoundingBox) -> bool:
    ((goal_x_min, goal_x_max, goal_y_min, goal_y_max),
     (test_x_min, test_x_max, test_y_min, test_y_max)) = goal, test
    return (goal_x_max < test_x_min or test_x_max < goal_x_min
            or goal_y_max < test_y_min or test_y_max < goal_y_min)


def from_iterable(points: Iterable[Point]) -> BoundingBox:
    iterator = iter(points)
    x_min, y_min = x_max, y_max = next(iterator)
    for x, y in iterator:
        x_min, x_max, y_min, y_max = (min(x_min, x), max(x_max, x),
                                      min(y_min, y), max(y_max, y))
    return x_min, x_max, y_min, y_max


def from_iterables(iterables: Iterable[Iterable[Point]]) -> BoundingBox:
    return from_iterable(flatten(iterables))
