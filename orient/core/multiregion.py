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
    contour_bounding_box = bounding_box.from_points(contour)
    disjoint, multiregion_max_x, events_queue = True, None, None
    for region in multiregion:
        region_bounding_box = bounding_box.from_points(region)
        if not bounding_box.disjoint_with(region_bounding_box,
                                          contour_bounding_box):
            if disjoint:
                disjoint = False
                _, multiregion_max_x, _, _ = region_bounding_box
                events_queue = EventsQueue()
                register_contour(events_queue, contour,
                                 from_test=True)
            else:
                _, region_max_x, _, _ = region_bounding_box
                multiregion_max_x = max(multiregion_max_x, region_max_x)
            register_region(events_queue, region,
                            from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, contour_max_x, _, _ = contour_bounding_box
    return process_linear_compound_queue(events_queue, min(contour_max_x,
                                                           multiregion_max_x))


def relate_region(multiregion: Multiregion, region: Region) -> Relation:
    if not multiregion:
        return Relation.DISJOINT
    region_bounding_box = bounding_box.from_points(region)
    all_disjoint, any_disjoint, multiregion_max_x, events_queue = (True, False,
                                                                   None, None)
    for sub_region in multiregion:
        sub_region_bounding_box = bounding_box.from_points(sub_region)
        if bounding_box.disjoint_with(region_bounding_box,
                                      sub_region_bounding_box):
            any_disjoint = True
        else:
            if all_disjoint:
                all_disjoint = False
                _, multiregion_max_x, _, _ = sub_region_bounding_box
                events_queue = EventsQueue()
                register_contour(events_queue, region,
                                 from_test=True)
            else:
                _, sub_region_max_x, _, _ = sub_region_bounding_box
                multiregion_max_x = max(multiregion_max_x, sub_region_max_x)
            register_region(events_queue, sub_region,
                            from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    _, region_max_x, _, _ = region_bounding_box
    relation = process_compound_queue(events_queue, min(multiregion_max_x,
                                                        region_max_x))
    return ((Relation.COMPONENT
             if relation is Relation.EQUAL
             else (Relation.OVERLAP
                   if relation in (Relation.COVER,
                                   Relation.ENCLOSES,
                                   Relation.COMPOSITE)
                   else relation))
            if any_disjoint
            else relation)


def relate_multiregion(goal: Multiregion, test: Multiregion) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    goal_bounding_box, test_bounding_box = (
        bounding_box.from_points(chain.from_iterable(goal)),
        bounding_box.from_points(chain.from_iterable(test)))
    if bounding_box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test=False)
    register(events_queue, test,
             from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_compound_queue(events_queue, min(goal_max_x, test_max_x))


def register(events_queue: EventsQueue, multiregion: Multiregion,
             *,
             from_test: bool) -> None:
    for region in multiregion:
        register_region(events_queue, region,
                        from_test=from_test)
