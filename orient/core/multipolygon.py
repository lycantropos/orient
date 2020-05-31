from typing import Iterator

from orient.hints import (Contour,
                          Multipolygon,
                          Multiregion,
                          Multisegment,
                          Point,
                          Polygon,
                          Region,
                          Segment)
from . import bounding_box
from .contour import to_segments as contour_to_segments
from .multiregion import (_relate_multiregion as relate_multiregions,
                          _relate_region as relate_region_to_multiregion,
                          to_segments as multiregion_to_segments)
from .polygon import (_relate_polygon as relate_polygon_to_polygon,
                      relate_point as relate_point_to_polygon,
                      relate_segment as relate_segment_to_polygon)
from .processing import process_linear_compound_queue
from .region import to_segments as region_to_segments
from .relation import Relation
from .sweep import ClosedSweeper
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
    multisegment_bounding_box = bounding_box.from_iterables(multisegment)
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for border, holes in multipolygon:
        polygon_bounding_box = bounding_box.from_iterable(border)
        if not bounding_box.disjoint_with(polygon_bounding_box,
                                          multisegment_bounding_box):
            if disjoint:
                disjoint = False
                _, multipolygon_max_x, _, _ = polygon_bounding_box
                sweeper = ClosedSweeper()
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
    contour_bounding_box = bounding_box.from_iterable(contour)
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for border, holes in multipolygon:
        polygon_bounding_box = bounding_box.from_iterable(border)
        if not bounding_box.disjoint_with(polygon_bounding_box,
                                          contour_bounding_box):
            if disjoint:
                disjoint = False
                _, multipolygon_max_x, _, _ = polygon_bounding_box
                sweeper = ClosedSweeper()
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
    region_bounding_box = bounding_box.from_iterable(region)
    relation_with_borders = relate_region_to_multiregion(
            _to_borders(multipolygon), region, region_bounding_box)
    if relation_with_borders in (Relation.DISJOINT,
                                 Relation.TOUCH,
                                 Relation.OVERLAP,
                                 Relation.COVER,
                                 Relation.ENCLOSES):
        return relation_with_borders
    elif (relation_with_borders is Relation.COMPOSITE
          or relation_with_borders is Relation.EQUAL):
        return (Relation.ENCLOSES
                if has_holes(multipolygon)
                else relation_with_borders)
    else:
        relation_with_holes = relate_region_to_multiregion(
                _to_holes(multipolygon), region, region_bounding_box)
        if relation_with_holes is Relation.DISJOINT:
            return relation_with_borders
        elif relation_with_holes is Relation.WITHIN:
            return Relation.DISJOINT
        elif relation_with_holes is Relation.TOUCH:
            return Relation.ENCLOSED
        elif (relation_with_holes is Relation.OVERLAP
              or relation_with_holes is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_holes in (Relation.ENCLOSED,
                                     Relation.COMPONENT,
                                     Relation.EQUAL):
            return Relation.TOUCH
        else:
            return Relation.OVERLAP


def relate_multiregion(multipolygon: Multipolygon,
                       multiregion: Multiregion) -> Relation:
    if not (multipolygon and multiregion):
        return Relation.DISJOINT
    multiregion_bounding_box = bounding_box.from_iterables(multiregion)
    relation_with_borders = relate_multiregions(
            _to_borders(multipolygon), multiregion,
            bounding_box.from_iterables(_to_borders(multipolygon)),
            multiregion_bounding_box)
    if relation_with_borders in (Relation.DISJOINT,
                                 Relation.TOUCH,
                                 Relation.OVERLAP,
                                 Relation.COVER,
                                 Relation.ENCLOSES):
        return relation_with_borders
    elif (relation_with_borders is Relation.COMPOSITE
          or relation_with_borders is Relation.EQUAL):
        return (Relation.ENCLOSES
                if has_holes(multipolygon)
                else relation_with_borders)
    elif has_holes(multipolygon):
        relation_with_holes = relate_multiregions(
                _to_holes(multipolygon), multiregion,
                bounding_box.from_iterables(_to_holes(multipolygon)),
                multiregion_bounding_box)
        if relation_with_holes is Relation.DISJOINT:
            return relation_with_borders
        elif relation_with_holes is Relation.WITHIN:
            return Relation.DISJOINT
        elif relation_with_holes is Relation.TOUCH:
            return Relation.ENCLOSED
        elif (relation_with_holes is Relation.OVERLAP
              or relation_with_holes is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_holes in (Relation.ENCLOSED,
                                     Relation.COMPONENT,
                                     Relation.EQUAL):
            return Relation.TOUCH
        else:
            return Relation.OVERLAP
    else:
        return relation_with_borders


def relate_polygon(multipolygon: Multipolygon, polygon: Polygon) -> Relation:
    border, holes = polygon
    return (_relate_polygon(multipolygon, border, holes,
                            bounding_box.from_iterable(border))
            if multipolygon
            else Relation.DISJOINT)


def _relate_polygon(multipolygon: Multipolygon,
                    border: Region,
                    holes: Multiregion,
                    border_bounding_box: bounding_box.BoundingBox) -> Relation:
    last_relation = None
    for sub_border, sub_holes in multipolygon:
        relation = relate_polygon_to_polygon(
                sub_border, sub_holes, bounding_box.from_iterable(sub_border),
                border, holes, border_bounding_box)
        if relation is Relation.DISJOINT:
            if last_relation is None:
                last_relation = relation
            elif (last_relation is not Relation.DISJOINT
                  and last_relation is not Relation.TOUCH):
                return Relation.OVERLAP
        elif relation is Relation.TOUCH:
            if last_relation is None or last_relation is Relation.DISJOINT:
                last_relation = relation
            elif last_relation is not Relation.TOUCH:
                return Relation.OVERLAP
        elif relation in (Relation.OVERLAP,
                          Relation.COMPONENT,
                          Relation.ENCLOSED,
                          Relation.WITHIN):
            return relation
        elif relation is Relation.EQUAL:
            return (relation
                    if len(multipolygon) == 1
                    else Relation.COMPONENT)
        elif last_relation is None:
            last_relation = relation
        elif (last_relation is Relation.DISJOINT
              or last_relation is Relation.TOUCH):
            return Relation.OVERLAP
        elif (relation is not last_relation
              and last_relation is not Relation.ENCLOSES):
            last_relation = Relation.ENCLOSES
    return (relate_region_to_multiregion(_to_borders(multipolygon), border,
                                         border_bounding_box)
            if last_relation is Relation.COMPOSITE
            else last_relation)


def relate_multipolygon(goal: Multipolygon, test: Multipolygon) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    last_relation = None
    for test_border, test_holes in test:
        relation = _relate_polygon(goal, test_border, test_holes,
                                   bounding_box.from_iterable(test_border))
        if relation is Relation.DISJOINT:
            if last_relation is None:
                last_relation = relation
        elif relation is Relation.TOUCH:
            if last_relation is None or last_relation is Relation.DISJOINT:
                last_relation = relation
            elif last_relation is not Relation.TOUCH:
                return Relation.OVERLAP
        elif relation in (Relation.OVERLAP,
                          Relation.COVER,
                          Relation.ENCLOSES,
                          Relation.COMPOSITE):
            return relation
        elif relation is Relation.EQUAL:
            return (relation
                    if len(test) == 1
                    else Relation.COMPOSITE)
        elif last_relation is None:
            last_relation = relation
        elif (last_relation is Relation.DISJOINT
              or last_relation is Relation.TOUCH):
            return Relation.OVERLAP
        elif (relation is not last_relation
              and last_relation is not Relation.ENCLOSED):
            last_relation = Relation.ENCLOSED
    return (relate_multiregions(_to_borders(goal), _to_borders(test),
                                bounding_box.from_iterables(_to_borders(goal)),
                                bounding_box.from_iterables(_to_borders(test)))
            if last_relation is Relation.COMPONENT
            else last_relation)


def has_holes(multipolygon: Multipolygon) -> bool:
    return any(holes for _, holes in multipolygon)


def _to_borders(multipolygon: Multipolygon) -> Iterator[Region]:
    return (border for border, _ in multipolygon)


def _to_holes(multipolygon: Multipolygon) -> Iterator[Region]:
    return flatten(holes for _, holes in multipolygon)
