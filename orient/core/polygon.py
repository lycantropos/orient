from orient.core import bounding_box
from orient.hints import (Point,
                          Polygon,
                          Segment)
from .contour import (contains_contour as contour_contains_contour,
                      register as register_contour,
                      relate_point as relate_point_to_contour,
                      relate_segment as relate_segment_to_contour)
from .events_queue import EventsQueue
from .relation import Relation
from .sweep import sweep


def relate_point(polygon: Polygon, point: Point) -> Relation:
    border, holes = polygon
    border_location = relate_point_to_contour(border, point)
    if border_location is Relation.WITHIN:
        for hole in holes:
            hole_relation = relate_point_to_contour(hole, point)
            if hole_relation is Relation.WITHIN:
                return Relation.DISJOINT
            elif hole_relation is Relation.COMPONENT:
                return Relation.COMPONENT
    return border_location


def relate_segment(polygon: Polygon, segment: Segment) -> Relation:
    border, holes = polygon
    border_relation = relate_segment_to_contour(border, segment)
    if (border_relation is Relation.WITHIN
            or border_relation is Relation.ENCLOSED):
        for hole in holes:
            hole_relation = relate_segment_to_contour(hole, segment)
            if hole_relation is Relation.WITHIN:
                return Relation.DISJOINT
            elif hole_relation is Relation.COMPONENT:
                return Relation.COMPONENT
            elif hole_relation is Relation.CROSS:
                return Relation.CROSS
            elif hole_relation is Relation.ENCLOSED:
                return Relation.TOUCH
            elif hole_relation is Relation.TOUCH:
                border_relation = Relation.ENCLOSED
    return border_relation


def contains_polygon(goal: Polygon, test: Polygon) -> bool:
    goal_border, goal_holes = goal
    test_border, test_holes = test
    if not contour_contains_contour(goal_border, test_border):
        return False
    elif not goal_holes:
        return True
    # we are checking that test polygon holes are supersets
    # of goal polygon holes which lie within test polygon border
    _, test_max_x, _, _ = bounding_box.from_points(test_border)
    events_queue = EventsQueue()
    for goal_hole in goal_holes:
        register_contour(events_queue, goal_hole,
                         from_test_contour=False)
    register_contour(events_queue, test_border,
                     from_test_contour=True)
    goal_holes_edges_in_test_border = [
        event.segment
        for event in sweep(events_queue, test_max_x)
        if not event.from_test_contour and event.in_intersection]
    events_queue.clear()
    for test_hole in test_holes:
        register_contour(events_queue, test_hole,
                         from_test_contour=False)
    for edge in goal_holes_edges_in_test_border:
        events_queue.register_segment(edge,
                                      from_test_contour=True)
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue, test_max_x))
