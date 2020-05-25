from typing import Iterable

from orient.hints import (Contour,
                          Multiregion,
                          Multisegment,
                          Point,
                          Region,
                          Segment)
from . import bounding_box
from .contour import to_segments as contour_to_segments
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import (relate_point as relate_point_to_region,
                     relate_segment as relate_segment_to_region,
                     to_segments as region_to_segments)
from .relation import Relation
from .sweep import ClosedSweeper
from .utils import flatten


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


def relate_multisegment(multiregion: Multiregion,
                        multisegment: Multisegment) -> Relation:
    if not (multisegment and multiregion):
        return Relation.DISJOINT
    multisegment_bounding_box = bounding_box.from_points(flatten(multisegment))
    disjoint, multiregion_max_x, sweeper = True, None, None
    for region in multiregion:
        region_bounding_box = bounding_box.from_points(region)
        if not bounding_box.disjoint_with(region_bounding_box,
                                          multisegment_bounding_box):
            if disjoint:
                disjoint = False
                _, multiregion_max_x, _, _ = region_bounding_box
                sweeper = ClosedSweeper()
                sweeper.register_segments(multisegment,
                                          from_test=True)
            else:
                _, region_max_x, _, _ = region_bounding_box
                multiregion_max_x = max(multiregion_max_x, region_max_x)
            sweeper.register_segments(region_to_segments(region),
                                      from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, multisegment_max_x, _, _ = multisegment_bounding_box
    return process_linear_compound_queue(sweeper, min(multisegment_max_x,
                                                      multiregion_max_x))


def relate_contour(multiregion: Multiregion, contour: Contour) -> Relation:
    contour_bounding_box = bounding_box.from_points(contour)
    disjoint, multiregion_max_x, sweeper = True, None, None
    for region in multiregion:
        region_bounding_box = bounding_box.from_points(region)
        if not bounding_box.disjoint_with(region_bounding_box,
                                          contour_bounding_box):
            if disjoint:
                disjoint = False
                _, multiregion_max_x, _, _ = region_bounding_box
                sweeper = ClosedSweeper()
                sweeper.register_segments(contour_to_segments(contour),
                                          from_test=True)
            else:
                _, region_max_x, _, _ = region_bounding_box
                multiregion_max_x = max(multiregion_max_x, region_max_x)
            sweeper.register_segments(region_to_segments(region),
                                      from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, contour_max_x, _, _ = contour_bounding_box
    return process_linear_compound_queue(sweeper, min(contour_max_x,
                                                      multiregion_max_x))


def relate_region(multiregion: Multiregion, region: Region) -> Relation:
    if not multiregion:
        return Relation.DISJOINT
    region_bounding_box = bounding_box.from_points(region)
    all_disjoint, any_disjoint, multiregion_max_x, sweeper = (True, False,
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
                sweeper = ClosedSweeper()
                sweeper.register_segments(region_to_segments(region),
                                          from_test=True)
            else:
                _, sub_region_max_x, _, _ = sub_region_bounding_box
                multiregion_max_x = max(multiregion_max_x, sub_region_max_x)
            sweeper.register_segments(region_to_segments(sub_region),
                                      from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    _, region_max_x, _, _ = region_bounding_box
    relation = process_compound_queue(sweeper, min(multiregion_max_x,
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
        bounding_box.from_points(flatten(goal)),
        bounding_box.from_points(flatten(test)))
    if bounding_box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    sweeper = ClosedSweeper()
    sweeper.register_segments(to_segments(goal),
                              from_test=False)
    sweeper.register_segments(to_segments(test),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


def to_segments(multiregion: Multiregion) -> Iterable[Segment]:
    for region in multiregion:
        yield from region_to_segments(region)
