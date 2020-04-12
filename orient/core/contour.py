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
    if bounding_box.disjoint_with(bounding_box.from_points(contour),
                                  bounding_box.from_points(segment)):
        return Relation.DISJOINT
    has_touch = has_cross = False
    previous_touch_index = previous_touch_edge_start = None
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
            edge_start, _ = edge
            if has_touch:
                if (not has_cross
                        and index - previous_touch_index == 1
                        and start not in edge and end not in edge
                        and (angle_orientation(end, start, edge_start)
                             is Orientation.COLLINEAR)
                        and not _segment_touches_consecutive_edges(
                                segment, edge, previous_touch_edge_start)):
                    has_cross = True
            else:
                has_touch = True
            previous_touch_index, previous_touch_edge_start = index, edge_start
        elif not has_cross and relation_with_edge is Relation.CROSS:
            has_cross = True
    if (not has_cross
            and has_touch
            and previous_touch_index == len(contour) - 1):
        first_edge_start = contour[-1]
        first_edge = first_edge_start, contour[0]
        if (relate_segments(first_edge, segment) is Relation.TOUCH
                and start not in first_edge and end not in first_edge
                and (angle_orientation(end, start, first_edge_start)
                     is Orientation.COLLINEAR)
                and not _segment_touches_consecutive_edges(
                        segment, first_edge, contour[-2])):
            has_cross = True
    return (Relation.CROSS
            if has_cross
            else (Relation.TOUCH
                  if has_touch
                  else Relation.DISJOINT))


def _segment_touches_consecutive_edges(segment: Segment,
                                       edge: Segment,
                                       previous_edge_start: Point) -> bool:
    start, end = segment
    edge_start, edge_end = edge
    edges_angle_orientation = angle_orientation(
            edge_end, edge_start, previous_edge_start)
    return ((angle_orientation(edge_end, edge_start, start)
             is edges_angle_orientation)
            is (angle_orientation(edge_end, edge_start, end)
                is edges_angle_orientation))


def orientation(contour: Contour) -> Orientation:
    index = min(range(len(contour)),
                key=contour.__getitem__)
    return angle_orientation(contour[index], contour[index - 1],
                             contour[(index + 1) % len(contour)])


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
    test_boundary_in_goal_interior = goal_boundary_in_test_interior = False
    has_cross = has_touch = False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweep(events_queue, test_max_x):
        if not has_cross and event.relationship is SegmentsRelationship.CROSS:
            has_cross = True
        if not has_touch and event.relationship is SegmentsRelationship.TOUCH:
            has_touch = True
        if (not test_boundary_in_goal_interior and event.from_test
                and event.relationship in (SegmentsRelationship.NONE,
                                           SegmentsRelationship.TOUCH)):
            test_boundary_in_goal_interior = True
        if (not goal_boundary_in_test_interior and not event.from_test
                and event.relationship in (SegmentsRelationship.NONE,
                                           SegmentsRelationship.TOUCH)):
            goal_boundary_in_test_interior = True
        if (test_is_subset_of_goal and event.from_test
                and not event.in_intersection
                and (event.relationship is not SegmentsRelationship.OVERLAP)):
            test_is_subset_of_goal = False
        if (goal_is_subset_of_test and not event.from_test
                and not event.in_intersection
                and (event.relationship is not SegmentsRelationship.OVERLAP)):
            goal_is_subset_of_test = False
    if goal_is_subset_of_test:
        goal_is_subset_of_test = not events_queue
    if goal_is_subset_of_test:
        return (Relation.EQUAL
                if test_is_subset_of_goal
                else (Relation.OVERLAP
                      if goal_boundary_in_test_interior
                      else Relation.COMPOSITE))
    elif test_is_subset_of_goal:
        return (Relation.OVERLAP
                if test_boundary_in_goal_interior
                else Relation.COMPONENT)
    else:
        return (Relation.CROSS
                if has_cross
                else (Relation.TOUCH
                      if has_touch
                      else Relation.DISJOINT))


def register(events_queue: EventsQueue, contour: Contour,
             *,
             from_test: bool) -> None:
    for edge in edges(contour):
        events_queue.register_segment(edge,
                                      from_test=from_test)


def edges(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
