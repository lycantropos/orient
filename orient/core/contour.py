from itertools import chain
from typing import (Iterable,
                    Sequence,
                    Tuple)

from robust.angular import (Orientation,
                            orientation as angle_orientation)
from robust.linear import (SegmentsRelationship,
                           segments_relationship)

from orient.hints import (Contour,
                          Coordinate,
                          Point,
                          Segment)
from . import bounding_box
from .events_queue import EventsQueue
from .relation import Relation
from .segment import relate_point as relate_point_to_segment
from .sweep import sweep


def relate_point(contour: Contour, point: Point) -> Relation:
    result = False
    _, point_y = point
    for edge in edges(contour):
        if relate_point_to_segment(edge, point) is not Relation.DISJOINT:
            return Relation.COMPONENT
        start, end = edge
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (angle_orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return (Relation.WITHIN
            if result
            else Relation.DISJOINT)


def relate_segment(contour: Contour, segment: Segment) -> Relation:
    if any(segments_relationship(segment, edge) is SegmentsRelationship.CROSS
           for edge in edges(contour)):
        return Relation.CROSS
    start, end = segment
    start_relation, end_relation = (relate_point(contour, start),
                                    relate_point(contour, end))
    if (start_relation is Relation.DISJOINT
            or end_relation is Relation.DISJOINT):
        if (start_relation is Relation.WITHIN
                or end_relation is Relation.WITHIN):
            return Relation.CROSS
        else:
            outsider = (start
                        if start_relation is Relation.DISJOINT
                        else end)
            try:
                _, start_index = min(
                        (_to_squared_distance_between_points(outsider, vertex),
                         index)
                        for index, vertex in enumerate(contour)
                        if (relate_point_to_segment(segment, vertex)
                            is not Relation.DISJOINT))
            except ValueError:
                return (Relation.TOUCH
                        if (start_relation is Relation.COMPONENT
                            or end_relation is Relation.COMPONENT)
                        else Relation.DISJOINT)
            _, end_index = max(
                    (_to_squared_distance_between_points(outsider, vertex),
                     index)
                    for index, vertex in enumerate(contour)
                    if (relate_point_to_segment(segment, vertex)
                        is not Relation.DISJOINT))
            min_index, max_index = _sort_pair(start_index, end_index)
            if (max_index - min_index <= 1
                    or not min_index and max_index == len(contour) - 1):
                return Relation.TOUCH
            first_part, second_part = _split(contour, min_index,
                                             max_index)
            return (Relation.CROSS
                    if orientation(first_part) is orientation(second_part)
                    else Relation.TOUCH)
    elif (start_relation is Relation.WITHIN
          and end_relation is Relation.WITHIN):
        return Relation.WITHIN
    elif (start_relation is Relation.WITHIN
          or end_relation is Relation.WITHIN):
        return Relation.ENCLOSED
    else:
        # both endpoints lie on contour
        start_index = end_index = None
        for index, edge in enumerate(edges(contour)):
            edge_start, edge_end = edge
            if edge_start == start:
                start_index = (index or len(contour)) - 1
                break
            elif edge_end == start:
                start_index = index
                break
            elif (relate_point_to_segment(edge, start)
                  is not Relation.DISJOINT):
                contour = contour[:]
                contour.insert(index, start)
                start_index = index
                break
        for index, edge in enumerate(edges(contour)):
            edge_start, edge_end = edge
            if edge_start == end:
                end_index = (index or len(contour)) - 1
                break
            elif edge_end == end:
                end_index = index
                break
            elif (relate_point_to_segment(edge, end)
                  is not Relation.DISJOINT):
                contour = contour[:]
                contour.insert(index, end)
                end_index = index
                if start_index > index:
                    start_index = (start_index + 1) % len(contour)
                break
        min_index, max_index = _sort_pair(start_index, end_index)
        if (max_index - min_index <= 1
                or not min_index and max_index == len(contour) - 1):
            return Relation.COMPONENT
        first_part, second_part = _split(contour, min_index, max_index)
        return (Relation.ENCLOSED
                if orientation(first_part) is orientation(second_part)
                else Relation.TOUCH)


def orientation(contour: Contour) -> Orientation:
    index = min(range(len(contour)),
                key=contour.__getitem__)
    previous_index, next_index = (index - 1 if index else len(contour) - 1,
                                  (index + 1) % len(contour))
    for _ in range(len(contour)):
        candidate = angle_orientation(contour[index], contour[previous_index],
                                      contour[next_index])
        if candidate is not Orientation.COLLINEAR:
            return candidate
        index, next_index = next_index, (next_index + 1) % len(contour)
    return Orientation.COLLINEAR


def _split(contour: Contour,
           start_index: int,
           stop_index: int) -> Tuple[Contour, Contour]:
    return (contour[start_index:stop_index + 1],
            contour[:start_index + 1] + contour[stop_index:])


def _to_squared_distance_between_points(left: Point,
                                        right: Point) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2


def _sort_pair(first: int, second: int) -> Tuple[int, int]:
    return (first, second) if first < second else (second, first)


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
    for edge in edges(contour):
        events_queue.register_segment(edge,
                                      from_test_contour=from_test_contour)


def edges(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
