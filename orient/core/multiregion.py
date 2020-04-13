from itertools import chain

from orient.hints import (Contour,
                          Multiregion,
                          Point,
                          Region,
                          Segment)
from . import bounding_box
from .contour import register as register_contour
from .events_queue import EventsQueue
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import (register as register_region,
                     relate_point as relate_point_to_region,
                     relate_segment as relate_segment_to_region)
from .relation import Relation


def relate_point(multiregion: Multiregion, point: Point) -> Relation:
    for region in multiregion:
        relation_with_region = relate_point_to_region(region, point)
        if relation_with_region is not Relation.DISJOINT:
            return relation_with_region
    return Relation.DISJOINT


def relate_segment(multiregion: Multiregion, segment: Segment) -> Relation:
    do_not_touch = True
    for region in multiregion:
        relation_with_region = relate_segment_to_region(region, segment)
        if relation_with_region in (Relation.CROSS,
                                    Relation.COMPONENT,
                                    Relation.ENCLOSED,
                                    Relation.WITHIN):
            return relation_with_region
        elif do_not_touch and relation_with_region is Relation.TOUCH:
            do_not_touch = False
    return (Relation.DISJOINT
            if do_not_touch
            else Relation.TOUCH)


def relate_contour(multiregion: Multiregion, contour: Contour) -> Relation:
    test_bounding_box = bounding_box.from_points(contour)
    overlapping_multiregion = [
        region
        for region in multiregion
        if not bounding_box.disjoint_with(bounding_box.from_points(region),
                                          test_bounding_box)]
    if not overlapping_multiregion:
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, overlapping_multiregion,
             from_test=False)
    register_contour(events_queue, contour,
                     from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return process_linear_compound_queue(events_queue, test_max_x)


def relate_region(multiregion: Multiregion, region: Region) -> Relation:
    if not multiregion:
        return Relation.DISJOINT
    test_bounding_box = bounding_box.from_points(region)
    overlapping_multiregion = [
        region
        for region in multiregion
        if not bounding_box.disjoint_with(bounding_box.from_points(region),
                                          test_bounding_box)]
    if not overlapping_multiregion:
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, multiregion,
             from_test=False)
    register_region(events_queue, region,
                    from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return process_compound_queue(events_queue, test_max_x)


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
    return process_compound_queue(events_queue, test_max_x)


def register(events_queue: EventsQueue, multiregion: Multiregion,
             *,
             from_test: bool) -> None:
    for region in multiregion:
        register_region(events_queue, region,
                        from_test=from_test)
