from robust.angular import (Orientation,
                            orientation as angle_orientation)
from robust.linear import SegmentsRelationship

from orient.hints import (Contour,
                          Coordinate,
                          Point,
                          Region,
                          Segment)
from . import bounding_box
from .contour import (edges as boundary_edges,
                      equal as contours_equal,
                      register as register_contour,
                      relate_segment as relate_segment_to_contour)
from .events_queue import EventsQueue
from .relation import Relation
from .segment import relate_point as relate_point_to_segment
from .sweep import sweep


def relate_point(region: Region, point: Point) -> Relation:
    if not bounding_box.contains_point(bounding_box.from_points(region),
                                       point):
        return Relation.DISJOINT
    result = False
    _, point_y = point
    for edge in boundary_edges(region):
        if relate_point_to_segment(edge, point) is Relation.COMPONENT:
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
    relation_with_contour = relate_segment_to_contour(region, segment)
    if (relation_with_contour is Relation.CROSS
            or relation_with_contour is Relation.COMPONENT):
        return relation_with_contour
    start, end = segment
    start_relation = relate_point(region, start)
    if relation_with_contour is Relation.DISJOINT:
        return (Relation.DISJOINT
                if start_relation is Relation.DISJOINT
                else Relation.WITHIN)
    else:
        return (Relation.TOUCH
                if (start_relation is Relation.DISJOINT
                    or relate_point(region, end) is Relation.DISJOINT)
                else Relation.ENCLOSED)


def relate_contour(region: Region, contour: Contour) -> Relation:
    test_bounding_box = bounding_box.from_points(contour)
    if bounding_box.disjoint_with(bounding_box.from_points(region),
                                  test_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour):
        return Relation.COMPONENT
    events_queue = EventsQueue()
    register(events_queue, region,
             from_test=False)
    register_contour(events_queue, contour,
                     from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return _process_linear_compound_queue(events_queue, test_max_x)


def _to_contour_relation(relation: Relation) -> Relation:
    if relation is Relation.OVERLAP:
        return Relation.CROSS
    elif relation is Relation.COVER:
        return Relation.DISJOINT
    elif relation is Relation.ENCLOSES or relation is Relation.COMPOSITE:
        return Relation.TOUCH
    elif relation is Relation.EQUAL:
        return Relation.COMPONENT
    else:
        return relation


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


def _process_linear_compound_queue(events_queue: EventsQueue,
                                   test_max_x: Coordinate) -> Relation:
    # ``goal`` is a compound object
    # ``test`` is a linear object
    has_cross = has_touch = False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweep(events_queue, test_max_x):
        if not has_cross and event.relationship is SegmentsRelationship.CROSS:
            has_cross = True
        if (not has_touch
                and event.relationship in (SegmentsRelationship.TOUCH,
                                           SegmentsRelationship.OVERLAP)):
            has_touch = True
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
        return (Relation.COMPONENT
                if test_is_subset_of_goal
                else (Relation.TOUCH
                      if has_touch
                      else Relation.DISJOINT))
    elif test_is_subset_of_goal:
        return (Relation.ENCLOSED
                if has_touch
                else Relation.WITHIN)
    else:
        return (Relation.CROSS
                if has_cross
                else (Relation.TOUCH
                      if has_touch
                      else Relation.DISJOINT))


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
