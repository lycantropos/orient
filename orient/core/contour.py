from itertools import chain
from typing import (Iterable,
                    Sequence)

from robust.angular import (Orientation,
                            orientation as angle_orientation)

from orient.hints import (Contour,
                          Point,
                          Segment)
from . import bounding_box
from .events_queue import EventsQueue
from .location import PointLocation
from .segment import contains_point as segment_contains_point
from .sweep import sweep


def contains_point(contour: Contour, point: Point) -> PointLocation:
    result = False
    _, point_y = point
    for edge in to_segments(contour):
        if segment_contains_point(edge, point) is not PointLocation.EXTERNAL:
            return PointLocation.BOUNDARY
        start, end = edge
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (angle_orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return (PointLocation.INTERNAL
            if result
            else PointLocation.EXTERNAL)


def contains_contour(goal: Contour, test: Contour) -> bool:
    test_bounding_box = bounding_box.from_points(test)
    if not bounding_box.contains_bounding_box(bounding_box.from_points(goal),
                                              test_bounding_box):
        return False
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    register(events_queue, test,
             from_test_contour=True)
    _, test_max_x, _, _ = test_bounding_box
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue, test_max_x))


def contains_contours(goal: Contour, tests: Sequence[Contour]) -> bool:
    if not tests:
        return True
    tests_bounding_box = bounding_box.from_points(chain.from_iterable(tests))
    if not bounding_box.contains_bounding_box(bounding_box.from_points(goal),
                                              tests_bounding_box):
        return False
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    for test in tests:
        register(events_queue, test,
                 from_test_contour=True)
    _, tests_max_x, _, _ = tests_bounding_box
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue, tests_max_x))


def register(events_queue: EventsQueue, contour: Contour,
             *,
             from_test_contour: bool) -> None:
    for segment in to_segments(contour):
        events_queue.register_segment(segment,
                                      from_test_contour=from_test_contour)


def to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
