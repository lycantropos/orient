from orient.core import bounding_box
from orient.hints import Polygon
from .contour import (contains_contour,
                      register as register_contour)
from .events_queue import EventsQueue
from .sweep import sweep


def contains_polygon(goal: Polygon, test: Polygon) -> bool:
    goal_border, goal_holes = goal
    test_border, test_holes = test
    test_bounding_box = bounding_box.from_points(test_border)
    if not (bounding_box.contains_bounding_box(
            bounding_box.from_points(goal_border), test_bounding_box)
            and contains_contour(goal_border, test_border)):
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
