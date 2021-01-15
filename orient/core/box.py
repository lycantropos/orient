from typing import Iterable

from ground.base import Context
from ground.hints import (Box,
                          Multisegment,
                          Point,
                          Segment)

from .utils import flatten


def contains_point(box: Box, point: Point) -> bool:
    return (box.min_x <= point.x <= box.max_x
            and box.min_y <= point.y <= box.max_y)


def disjoint_with(goal: Box, test: Box) -> bool:
    return (goal.max_x < test.min_x or test.max_x < goal.min_x
            or goal.max_y < test.min_y or test.max_y < goal.min_y)


def from_iterable(points: Iterable[Point],
                  *,
                  context: Context) -> Box:
    iterator = iter(points)
    point = next(iterator)
    min_x, min_y = max_x, max_y = point.x, point.y
    for point in iterator:
        min_x, max_x, min_y, max_y = (min(min_x, point.x), max(max_x, point.x),
                                      min(min_y, point.y), max(max_y, point.y))
    return context.box_cls(min_x, max_x, min_y, max_y)


def from_iterables(iterables: Iterable[Iterable[Point]],
                   *,
                   context: Context) -> Box:
    return from_iterable(flatten(iterables),
                         context=context)


def from_multisegment(multisegment: Multisegment,
                      *,
                      context: Context) -> Box:
    return from_iterable(flatten((segment.start, segment.end)
                                 for segment in multisegment.segments),
                         context=context)


def from_segment(segment: Segment,
                 *,
                 context: Context) -> Box:
    start, end = segment.start, segment.end
    return context.box_cls(min(start.x, end.x), max(start.x, end.x),
                           min(start.y, end.y), max(start.y, end.y))
