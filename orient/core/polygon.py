from orient.core import bounding_box
from orient.hints import (Polygon,
                          Segment)
from .contour import (contains_contour as contour_contains_contour,
                      contains_segment as contour_contains_segment,
                      register as register_contour)
from .events_queue import EventsQueue
from .location import SegmentLocation
from .sweep import sweep


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
    test_bounding_box = bounding_box.from_points(test_border)
    if not (bounding_box.contains_bounding_box(
            bounding_box.from_points(goal_border), test_bounding_box)
            and contour_contains_contour(goal_border, test_border)):
        return False
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    register(events_queue, test,
             from_test_contour=True)
    _, test_max_x, _, _ = test_bounding_box
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue, test_max_x))


def register(events_queue: EventsQueue, polygon: Polygon,
             *,
             from_test_contour: bool) -> None:
    border, holes = polygon
    register_contour(events_queue, border,
                     from_test_contour=from_test_contour)
    for hole in holes:
        register_contour(events_queue, hole,
                         from_test_contour=from_test_contour)
