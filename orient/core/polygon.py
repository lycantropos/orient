from orient.core import bounding_box
from orient.hints import (Point,
                          Polygon,
                          Segment)
from .contour import (contains_contour as contour_contains_contour,
                      contains_point as contour_contains_point,
                      contains_segment as contour_contains_segment,
                      register as register_contour)
from .events_queue import EventsQueue
from .location import (PointLocation,
                       SegmentLocation)
from .sweep import sweep


def contains_point(polygon: Polygon, point: Point) -> PointLocation:
    border, holes = polygon
    border_location = contour_contains_point(border, point)
    if border_location is PointLocation.INTERNAL:
        for hole in holes:
            hole_location = contour_contains_point(hole, point)
            if hole_location is PointLocation.INTERNAL:
                return PointLocation.EXTERNAL
            elif hole_location is PointLocation.BOUNDARY:
                return PointLocation.BOUNDARY
    return border_location


def contains_segment(polygon: Polygon, segment: Segment) -> SegmentLocation:
    border, holes = polygon
    border_location = contour_contains_segment(border, segment)
    if (border_location is SegmentLocation.INTERNAL
            or border_location is SegmentLocation.ENCLOSED):
        for hole in holes:
            hole_location = contour_contains_segment(hole, segment)
            if hole_location is SegmentLocation.INTERNAL:
                return SegmentLocation.EXTERNAL
            elif hole_location is SegmentLocation.BOUNDARY:
                return SegmentLocation.BOUNDARY
            elif hole_location is SegmentLocation.CROSS:
                return SegmentLocation.CROSS
            elif hole_location is SegmentLocation.ENCLOSED:
                return SegmentLocation.TOUCH
            elif hole_location is SegmentLocation.TOUCH:
                border_location = SegmentLocation.ENCLOSED
    return border_location


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
