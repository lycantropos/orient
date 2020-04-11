from typing import Tuple

from robust.angular import (Orientation,
                            orientation as angle_orientation)
from robust.linear import (SegmentsRelationship,
                           segments_relationship)

from orient.hints import (Coordinate,
                          Point,
                          Region,
                          Segment)
from . import bounding_box
from .contour import (edges as boundary_edges,
                      equal as contours_equal,
                      orientation as boundary_orientation,
                      register as register_contour)
from .events_queue import EventsQueue
from .relation import Relation
from .segment import relate_point as relate_point_to_segment
from .sweep import sweep


def relate_point(region: Region, point: Point) -> Relation:
    result = False
    _, point_y = point
    for edge in boundary_edges(region):
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


def relate_segment(region: Region, segment: Segment) -> Relation:
    if any(segments_relationship(segment, edge) is SegmentsRelationship.CROSS
           for edge in boundary_edges(region)):
        return Relation.CROSS
    start, end = segment
    start_relation, end_relation = (relate_point(region, start),
                                    relate_point(region, end))
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
                        for index, vertex in enumerate(region)
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
                    for index, vertex in enumerate(region)
                    if (relate_point_to_segment(segment, vertex)
                        is not Relation.DISJOINT))
            min_index, max_index = _sort_pair(start_index, end_index)
            if (max_index - min_index <= 1
                    or not min_index and max_index == len(region) - 1):
                return Relation.TOUCH
            first_part, second_part = _split(region, min_index,
                                             max_index)
            return (Relation.CROSS
                    if (boundary_orientation(first_part)
                        is boundary_orientation(second_part))
                    else Relation.TOUCH)
    elif start_relation is Relation.WITHIN and end_relation is Relation.WITHIN:
        return Relation.WITHIN
    elif start_relation is Relation.WITHIN or end_relation is Relation.WITHIN:
        return Relation.ENCLOSED
    else:
        # both endpoints lie in region
        start_index = end_index = None
        for index, edge in enumerate(boundary_edges(region)):
            edge_start, edge_end = edge
            if edge_start == start:
                start_index = (index or len(region)) - 1
                break
            elif edge_end == start:
                start_index = index
                break
            elif relate_point_to_segment(edge, start) is not Relation.DISJOINT:
                region = region[:]
                region.insert(index, start)
                start_index = index
                break
        for index, edge in enumerate(boundary_edges(region)):
            edge_start, edge_end = edge
            if edge_start == end:
                end_index = (index or len(region)) - 1
                break
            elif edge_end == end:
                end_index = index
                break
            elif relate_point_to_segment(edge, end) is not Relation.DISJOINT:
                region = region[:]
                region.insert(index, end)
                end_index = index
                if start_index > index:
                    start_index = (start_index + 1) % len(region)
                break
        min_index, max_index = _sort_pair(start_index, end_index)
        if (max_index - min_index <= 1
                or not min_index and max_index == len(region) - 1):
            return Relation.COMPONENT
        first_part, second_part = _split(region, min_index, max_index)
        return (Relation.ENCLOSED
                if (boundary_orientation(first_part)
                    is boundary_orientation(second_part))
                else Relation.TOUCH)


def _split(region: Region,
           start_index: int,
           stop_index: int) -> Tuple[Region, Region]:
    return (region[start_index:stop_index + 1],
            region[:start_index + 1] + region[stop_index:])


def _to_squared_distance_between_points(left: Point,
                                        right: Point) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2


def _sort_pair(first: int, second: int) -> Tuple[int, int]:
    return (first, second) if first < second else (second, first)


def relate_region(goal: Region, test: Region) -> Relation:
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


equal = contours_equal


def _process_queue(events_queue: EventsQueue,
                   test_max_x: Coordinate) -> Relation:
    test_boundary_in_goal_interior = goal_boundary_in_test_interior = False
    boundaries_do_not_intersect, overlaps = True, False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweep(events_queue, test_max_x):
        if event.relationship is SegmentsRelationship.CROSS:
            return Relation.OVERLAP
        if (boundaries_do_not_intersect
                and event.relationship is not SegmentsRelationship.NONE):
            boundaries_do_not_intersect = False
        if (not overlaps and event.in_intersection
                and event.relationship is not SegmentsRelationship.OVERLAP):
            overlaps = True
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
    if boundaries_do_not_intersect:
        return (Relation.WITHIN
                if test_is_subset_of_goal
                else (Relation.COVER
                      if goal_is_subset_of_test
                      else (Relation.OVERLAP
                            if overlaps
                            else Relation.DISJOINT)))
    elif test_is_subset_of_goal:
        return (Relation.ENCLOSED
                if test_boundary_in_goal_interior
                else (Relation.EQUAL
                      if goal_is_subset_of_test
                      else Relation.COMPONENT))
    elif goal_is_subset_of_test:
        return (Relation.ENCLOSES
                if goal_boundary_in_test_interior
                else Relation.COMPOSITE)
    else:
        return (Relation.OVERLAP
                if overlaps
                else Relation.TOUCH)


register = register_contour
