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
    return (_relate_multisegment(multiregion, multisegment,
                                 bounding_box.from_iterables(multisegment))
            if multisegment and multiregion
            else Relation.DISJOINT)


def _relate_multisegment(multiregion: Multiregion,
                         multisegment: Multisegment,
                         multisegment_bounding_box: bounding_box.BoundingBox
                         ) -> Relation:
    disjoint, multiregion_max_x, sweeper = True, None, None
    for region in multiregion:
        region_bounding_box = bounding_box.from_iterable(region)
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
    return (_relate_contour(multiregion, contour,
                            bounding_box.from_iterable(contour))
            if multiregion
            else Relation.DISJOINT)


def _relate_contour(multiregion: Multiregion,
                    contour: Contour,
                    contour_bounding_box: bounding_box.BoundingBox
                    ) -> Relation:
    disjoint, multiregion_max_x, sweeper = True, None, None
    for region in multiregion:
        region_bounding_box = bounding_box.from_iterable(region)
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
    return (_relate_region(multiregion, region,
                           bounding_box.from_iterable(region))
            if multiregion
            else Relation.DISJOINT)


def _relate_region(goal_regions: Iterable[Region],
                   region: Region,
                   region_bounding_box: bounding_box.BoundingBox) -> Relation:
    all_disjoint, any_disjoint, goal_regions_max_x, sweeper = (True, False,
                                                               None, None)
    for goal_region in goal_regions:
        goal_region_bounding_box = bounding_box.from_iterable(goal_region)
        if bounding_box.disjoint_with(region_bounding_box,
                                      goal_region_bounding_box):
            any_disjoint = True
        else:
            if all_disjoint:
                all_disjoint = False
                _, goal_regions_max_x, _, _ = goal_region_bounding_box
                sweeper = ClosedSweeper()
                sweeper.register_segments(region_to_segments(region),
                                          from_test=True)
            else:
                _, goal_region_max_x, _, _ = goal_region_bounding_box
                goal_regions_max_x = max(goal_regions_max_x, goal_region_max_x)
            sweeper.register_segments(region_to_segments(goal_region),
                                      from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    _, region_max_x, _, _ = region_bounding_box
    relation = process_compound_queue(sweeper, min(goal_regions_max_x,
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
    return (_relate_multiregion(goal, test,
                                bounding_box.from_iterables(goal),
                                bounding_box.from_iterables(test))
            if goal and test
            else Relation.DISJOINT)


def _relate_multiregion(goal: Iterable[Region],
                        test: Iterable[Region],
                        goal_bounding_box: bounding_box.BoundingBox,
                        test_bounding_box: bounding_box.BoundingBox
                        ) -> Relation:
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


def to_segments(regions: Iterable[Region]) -> Iterable[Segment]:
    for region in regions:
        yield from region_to_segments(region)
