from itertools import chain

from orient.hints import (Contour,
                          Multicontour)
from . import bounding_box
from .contour import (_process_queue,
                      register as register_contour)
from .events_queue import EventsQueue
from .relation import Relation


def relate_contour(goal: Multicontour, test: Contour) -> Relation:
    if not goal:
        return Relation.DISJOINT
    test_bounding_box = bounding_box.from_points(test)
    if bounding_box.disjoint_with(
            bounding_box.from_points(chain.from_iterable(goal)),
            test_bounding_box):
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    register_contour(events_queue, test,
                     from_test_contour=True)
    _, test_max_x, _, _ = test_bounding_box
    return _process_queue(events_queue, test_max_x)


def relate_multicontour(goal: Multicontour, test: Multicontour) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    test_bounding_box = bounding_box.from_points(chain.from_iterable(test))
    if bounding_box.disjoint_with(
            bounding_box.from_points(chain.from_iterable(goal)),
            test_bounding_box):
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    register(events_queue, test,
             from_test_contour=True)
    _, test_max_x, _, _ = test_bounding_box
    return _process_queue(events_queue, test_max_x)


def register(events_queue: EventsQueue, multicontour: Multicontour,
             *,
             from_test_contour: bool) -> None:
    for contour in multicontour:
        register_contour(events_queue, contour,
                         from_test_contour=from_test_contour)
