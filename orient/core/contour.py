from typing import Iterable

from robust.angular import (Orientation,
                            orientation as angle_orientation)
from robust.linear import (SegmentsRelationship)

from orient.hints import (Contour,
                          Coordinate,
                          Point,
                          Segment)
from . import bounding_box
from .events_queue import EventsQueue
from .relation import Relation
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)
from .sweep import sweep


def relate_point(contour: Contour, point: Point) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(edge, point) is Relation.DISJOINT
                   for edge in edges(contour))
            else Relation.COMPONENT)


def relate_segment(contour: Contour, segment: Segment) -> Relation:
    has_touch = has_cross = False
    previous_touch_index = None
    start, end = segment
    for index, edge in enumerate(edges(contour)):
        relation_with_edge = relate_segments(edge, segment)
        if (relation_with_edge is Relation.COMPONENT
                or relation_with_edge is Relation.EQUAL):
            return Relation.COMPONENT
        elif (relation_with_edge is Relation.OVERLAP
              or relation_with_edge is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_edge is Relation.TOUCH:
            if has_touch:
                if (not has_cross and index - previous_touch_index == 1
                        and start not in edge and end not in edge):
                    has_cross = True
            else:
                has_touch = True
            previous_touch_index = index
        elif not has_cross and relation_with_edge is Relation.CROSS:
            has_cross = True
    if (not has_cross
            and has_touch
            and previous_touch_index == len(contour) - 1):
        first_edge = contour[-1], contour[0]
        if (relate_segments(first_edge, segment) is Relation.TOUCH
                and start not in first_edge and end not in first_edge):
            has_cross = True
    return (Relation.CROSS
            if has_cross
            else (Relation.TOUCH
                  if has_touch
                  else Relation.DISJOINT))


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


def relate_contour(goal: Contour, test: Contour) -> Relation:
    test_bounding_box = bounding_box.from_points(test)
    if bounding_box.disjoint_with(bounding_box.from_points(goal),
                                  test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test):
        return Relation.EQUAL
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test=False)
    register(events_queue, test,
             from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return _process_queue(events_queue, test_max_x)


def equal(left: Contour, right: Contour) -> bool:
    if len(left) != len(right):
        return False
    if orientation(left) is not orientation(right):
        right = right[:1] + right[:0:-1]
    size = len(left)
    start = 0
    while start < size:
        try:
            index = right.index(left[0], start)
        except ValueError:
            return False
        else:
            left_index = 0
            for left_index, right_index in zip(range(size),
                                               range(index, size)):
                if left[left_index] != right[right_index]:
                    break
            else:
                for left_index, right_index in zip(range(left_index + 1, size),
                                                   range(index)):
                    if left[left_index] != right[right_index]:
                        break
                else:
                    return True
            start = index + 1


def _process_queue(events_queue: EventsQueue,
                   test_max_x: Coordinate) -> Relation:
    has_cross = has_touch = False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweep(events_queue, test_max_x):
        if event.relationship is SegmentsRelationship.OVERLAP:
            return Relation.OVERLAP
        if not has_cross and event.relationship is SegmentsRelationship.CROSS:
            has_cross = True
        if not has_touch and event.relationship is SegmentsRelationship.TOUCH:
            has_touch = True
        if (test_is_subset_of_goal and event.from_test
                and not event.in_intersection
                and (event.relationship is not SegmentsRelationship.OVERLAP)):
            test_is_subset_of_goal = False
        if (goal_is_subset_of_test and not event.from_test
                and not event.in_intersection
                and (event.relationship is not SegmentsRelationship.OVERLAP)):
            goal_is_subset_of_test = False
    return (Relation.EQUAL
            if goal_is_subset_of_test and test_is_subset_of_goal
            else (Relation.CROSS
                  if has_cross
                  else (Relation.TOUCH
                        if has_touch
                        else Relation.DISJOINT)))


def register(events_queue: EventsQueue, contour: Contour,
             *,
             from_test: bool) -> None:
    for edge in edges(contour):
        events_queue.register_segment(edge,
                                      from_test=from_test)


def edges(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
