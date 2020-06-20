from typing import Iterable

from orient.hints import (Contour,
                          Multiregion,
                          Multisegment,
                          Point,
                          Region,
                          Segment)
from . import bounding
from .contour import to_segments as contour_to_segments
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import (relate_point as relate_point_to_region,
                     relate_segment as relate_segment_to_region,
                     to_oriented_segments as region_to_oriented_segments)
from .relation import Relation
from .sweep import CompoundSweeper


def relate_point(multiregion: Multiregion, point: Point) -> Relation:
    for region in multiregion:
        relation_with_region = relate_point_to_region(region, point)
        if relation_with_region is not Relation.DISJOINT:
            return relation_with_region
    return Relation.DISJOINT


def relate_segment(multiregion: Multiregion, segment: Segment) -> Relation:
    return (relate_segment_to_region(multiregion[0], segment)
            if len(multiregion) == 1
            else _relate_multisegment(multiregion, [segment],
                                      bounding.box_from_iterable(segment)))


def relate_multisegment(multiregion: Multiregion,
                        multisegment: Multisegment) -> Relation:
    return (_relate_multisegment(multiregion, multisegment,
                                 bounding.box_from_iterables(multisegment))
            if multisegment and multiregion
            else Relation.DISJOINT)


def _relate_multisegment(multiregion: Multiregion,
                         multisegment: Multisegment,
                         multisegment_bounding_box: bounding.Box) -> Relation:
    disjoint, multiregion_max_x, sweeper = True, None, None
    for region in multiregion:
        region_bounding_box = bounding.box_from_iterable(region)
        if not bounding.box_disjoint_with(region_bounding_box,
                                          multisegment_bounding_box):
            if disjoint:
                disjoint = False
                _, multiregion_max_x, _, _ = region_bounding_box
                sweeper = CompoundSweeper()
                sweeper.register_segments(multisegment,
                                          from_test=True)
            else:
                _, region_max_x, _, _ = region_bounding_box
                multiregion_max_x = max(multiregion_max_x, region_max_x)
            sweeper.register_segments(region_to_oriented_segments(region),
                                      from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, multisegment_max_x, _, _ = multisegment_bounding_box
    return process_linear_compound_queue(sweeper, min(multisegment_max_x,
                                                      multiregion_max_x))


def relate_contour(multiregion: Multiregion, contour: Contour) -> Relation:
    return (_relate_contour(multiregion, contour,
                            bounding.box_from_iterable(contour))
            if multiregion
            else Relation.DISJOINT)


def _relate_contour(multiregion: Multiregion,
                    contour: Contour,
                    contour_bounding_box: bounding.Box) -> Relation:
    disjoint, multiregion_max_x, sweeper = True, None, None
    for region in multiregion:
        region_bounding_box = bounding.box_from_iterable(region)
        if not bounding.box_disjoint_with(region_bounding_box,
                                          contour_bounding_box):
            if disjoint:
                disjoint = False
                _, multiregion_max_x, _, _ = region_bounding_box
                sweeper = CompoundSweeper()
                sweeper.register_segments(contour_to_segments(contour),
                                          from_test=True)
            else:
                _, region_max_x, _, _ = region_bounding_box
                multiregion_max_x = max(multiregion_max_x, region_max_x)
            sweeper.register_segments(region_to_oriented_segments(region),
                                      from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, contour_max_x, _, _ = contour_bounding_box
    return process_linear_compound_queue(sweeper, min(contour_max_x,
                                                      multiregion_max_x))


def relate_region(multiregion: Multiregion, region: Region) -> Relation:
    return (_relate_region(multiregion, region,
                           bounding.box_from_iterable(region))
            if multiregion
            else Relation.DISJOINT)


def _relate_region(goal_regions: Iterable[Region],
                   region: Region,
                   region_bounding_box: bounding.Box) -> Relation:
    all_disjoint, none_disjoint, goal_regions_max_x, sweeper = (True, True,
                                                                None, None)
    for goal_region in goal_regions:
        goal_region_bounding_box = bounding.box_from_iterable(goal_region)
        if bounding.box_disjoint_with(region_bounding_box,
                                      goal_region_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                _, goal_regions_max_x, _, _ = goal_region_bounding_box
                sweeper = CompoundSweeper()
                sweeper.register_segments(region_to_oriented_segments(region),
                                          from_test=True)
            else:
                _, goal_region_max_x, _, _ = goal_region_bounding_box
                goal_regions_max_x = max(goal_regions_max_x, goal_region_max_x)
            sweeper.register_segments(region_to_oriented_segments(goal_region),
                                      from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    _, region_max_x, _, _ = region_bounding_box
    relation = process_compound_queue(sweeper, min(goal_regions_max_x,
                                                   region_max_x))
    return (relation
            if none_disjoint
            else (Relation.COMPONENT
                  if relation is Relation.EQUAL
                  else (Relation.OVERLAP
                        if relation in (Relation.COVER,
                                        Relation.ENCLOSES,
                                        Relation.COMPOSITE)
                        else relation)))


def relate_multiregion(goal: Multiregion, test: Multiregion) -> Relation:
    return (_relate_multiregion(goal, test,
                                bounding.box_from_iterables(goal),
                                bounding.box_from_iterables(test))
            if goal and test
            else Relation.DISJOINT)


def _relate_multiregion(goal: Iterable[Region],
                        test: Iterable[Region],
                        goal_bounding_box: bounding.Box,
                        test_bounding_box: bounding.Box) -> Relation:
    if bounding.box_disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(goal),
                              from_test=False)
    sweeper.register_segments(to_oriented_segments(test),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


def to_oriented_segments(regions: Iterable[Region],
                         *,
                         clockwise: bool = False) -> Iterable[Segment]:
    for region in regions:
        yield from region_to_oriented_segments(region,
                                               clockwise=clockwise)
