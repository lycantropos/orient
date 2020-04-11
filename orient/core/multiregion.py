from itertools import chain

from orient.hints import (Multiregion,
                          Region)
from . import bounding_box
from .events_queue import EventsQueue
from .region import (_process_queue,
                     register as register_region)
from .relation import Relation


def relate_region(goal: Multiregion, test: Region) -> Relation:
    if not goal:
        return Relation.DISJOINT
    test_bounding_box = bounding_box.from_points(test)
    if bounding_box.disjoint_with(
            bounding_box.from_points(chain.from_iterable(goal)),
            test_bounding_box):
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test=False)
    register_region(events_queue, test,
                    from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return _process_queue(events_queue, test_max_x)


def relate_multiregion(goal: Multiregion, test: Multiregion) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    test_bounding_box = bounding_box.from_points(chain.from_iterable(test))
    if bounding_box.disjoint_with(
            bounding_box.from_points(chain.from_iterable(goal)),
            test_bounding_box):
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test=False)
    register(events_queue, test,
             from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return _process_queue(events_queue, test_max_x)


def register(events_queue: EventsQueue, multiregion: Multiregion,
             *,
             from_test: bool) -> None:
    for region in multiregion:
        register_region(events_queue, region,
                        from_test=from_test)
