from typing import Iterable

from orient.hints import (Contour,
                          Multipolygon,
                          Multiregion,
                          Multisegment,
                          Point,
                          Polygon,
                          Region,
                          Segment)
from . import bounding
from .contour import to_segments as contour_to_segments
from .multiregion import to_segments as multiregion_to_segments
from .polygon import (relate_point as relate_point_to_polygon,
                      relate_segment as relate_segment_to_polygon,
                      to_segments as polygon_to_segments)
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import to_segments as region_to_segments
from .relation import Relation
from .sweep import CompoundSweeper
from .utils import flatten


def relate_point(multipolygon: Multipolygon, point: Point) -> Relation:
    for polygon in multipolygon:
        relation_with_polygon = relate_point_to_polygon(polygon, point)
        if relation_with_polygon is not Relation.DISJOINT:
            return relation_with_polygon
    return Relation.DISJOINT


def relate_segment(multipolygon: Multipolygon, segment: Segment) -> Relation:
    do_not_touch = True
    for polygon in multipolygon:
        relation_with_polygon = relate_segment_to_polygon(polygon, segment)
        if relation_with_polygon in (Relation.CROSS,
                                     Relation.COMPONENT,
                                     Relation.ENCLOSED,
                                     Relation.WITHIN):
            return relation_with_polygon
        elif do_not_touch and relation_with_polygon is Relation.TOUCH:
            do_not_touch = False
    return (Relation.DISJOINT
            if do_not_touch
            else Relation.TOUCH)


def relate_multisegment(multipolygon: Multipolygon,
                        multisegment: Multisegment) -> Relation:
    if not (multisegment and multipolygon):
        return Relation.DISJOINT
    multisegment_bounding_box = bounding.box_from_iterables(multisegment)
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for border, holes in multipolygon:
        polygon_bounding_box = bounding.box_from_iterable(border)
        if not bounding.box_disjoint_with(polygon_bounding_box,
                                          multisegment_bounding_box):
            if disjoint:
                disjoint = False
                _, multipolygon_max_x, _, _ = polygon_bounding_box
                sweeper = CompoundSweeper()
                sweeper.register_segments(multisegment,
                                          from_test=True)
            else:
                _, polygon_max_x, _, _ = polygon_bounding_box
                multipolygon_max_x = max(multipolygon_max_x, polygon_max_x)
            sweeper.register_segments(region_to_segments(border),
                                      from_test=False)
            sweeper.register_segments(multiregion_to_segments(holes),
                                      from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, multisegment_max_x, _, _ = multisegment_bounding_box
    return process_linear_compound_queue(sweeper, min(multisegment_max_x,
                                                      multipolygon_max_x))


def relate_contour(multipolygon: Multipolygon, contour: Contour) -> Relation:
    if not multipolygon:
        return Relation.DISJOINT
    contour_bounding_box = bounding.box_from_iterable(contour)
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for border, holes in multipolygon:
        polygon_bounding_box = bounding.box_from_iterable(border)
        if not bounding.box_disjoint_with(polygon_bounding_box,
                                          contour_bounding_box):
            if disjoint:
                disjoint = False
                _, multipolygon_max_x, _, _ = polygon_bounding_box
                sweeper = CompoundSweeper()
                sweeper.register_segments(contour_to_segments(contour),
                                          from_test=True)
            else:
                _, polygon_max_x, _, _ = polygon_bounding_box
                multipolygon_max_x = max(multipolygon_max_x, polygon_max_x)
            sweeper.register_segments(region_to_segments(border),
                                      from_test=False)
            sweeper.register_segments(multiregion_to_segments(holes),
                                      from_test=False)
    if disjoint:
        return Relation.DISJOINT
    _, contour_max_x, _, _ = contour_bounding_box
    return process_linear_compound_queue(sweeper, min(contour_max_x,
                                                      multipolygon_max_x))


def relate_region(multipolygon: Multipolygon, region: Region) -> Relation:
    if not multipolygon:
        return Relation.DISJOINT
    region_bounding_box = bounding.box_from_iterable(region)
    all_disjoint, none_disjoint, multipolygon_max_x, sweeper = (True, True,
                                                                None, None)
    for border, holes in multipolygon:
        polygon_bounding_box = bounding.box_from_iterable(border)
        if bounding.box_disjoint_with(region_bounding_box,
                                      polygon_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                _, multipolygon_max_x, _, _ = polygon_bounding_box
                sweeper = CompoundSweeper()
                sweeper.register_segments(region_to_segments(region),
                                          from_test=True)
            else:
                _, polygon_max_x, _, _ = polygon_bounding_box
                multipolygon_max_x = max(multipolygon_max_x, polygon_max_x)
            sweeper.register_segments(region_to_segments(border),
                                      from_test=False)
            sweeper.register_segments(multiregion_to_segments(holes),
                                      from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    _, region_max_x, _, _ = region_bounding_box
    relation = process_compound_queue(sweeper, min(multipolygon_max_x,
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


def relate_multiregion(multipolygon: Multipolygon,
                       multiregion: Multiregion) -> Relation:
    if not (multipolygon and multiregion):
        return Relation.DISJOINT
    multiregion_bounding_box = bounding.box_from_iterables(multiregion)
    multipolygon_bounding_box = bounding.box_from_iterables(
            _to_borders(multipolygon))
    if bounding.box_disjoint_with(multipolygon_bounding_box,
                                  multiregion_bounding_box):
        return Relation.DISJOINT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_segments(multipolygon),
                              from_test=False)
    sweeper.register_segments(multiregion_to_segments(multiregion),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (multipolygon_bounding_box,
                                                    multiregion_bounding_box)
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


def relate_polygon(multipolygon: Multipolygon, polygon: Polygon) -> Relation:
    border, _ = polygon
    multipolygon_bounding_box = bounding.box_from_iterables(
            _to_borders(multipolygon))
    polygon_bounding_box = bounding.box_from_iterable(border)
    if bounding.box_disjoint_with(multipolygon_bounding_box,
                                  polygon_bounding_box):
        return Relation.DISJOINT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_segments(multipolygon),
                              from_test=False)
    sweeper.register_segments(polygon_to_segments(polygon),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (multipolygon_bounding_box,
                                                    polygon_bounding_box)
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


def relate_multipolygon(goal: Multipolygon, test: Multipolygon) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    goal_bounding_box = bounding.box_from_iterables(_to_borders(goal))
    test_bounding_box = bounding.box_from_iterables(_to_borders(test))
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_segments(goal),
                              from_test=False)
    sweeper.register_segments(to_segments(test),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


def to_segments(polygons: Iterable[Polygon]) -> Iterable[Segment]:
    for polygon in polygons:
        yield from polygon_to_segments(polygon)


def has_holes(multipolygon: Multipolygon) -> bool:
    return any(holes for _, holes in multipolygon)


def _to_borders(multipolygon: Multipolygon) -> Iterable[Region]:
    return (border for border, _ in multipolygon)


def _to_holes(multipolygon: Multipolygon) -> Iterable[Region]:
    return flatten(holes for _, holes in multipolygon)
