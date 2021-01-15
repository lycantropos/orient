from typing import Iterable

from ground.base import (Context,
                         Relation)

from . import box
from .contour import to_segments as contour_to_segments
from .hints import (Contour,
                    Multipolygon,
                    Multiregion,
                    Multisegment,
                    Point,
                    Polygon,
                    Region,
                    Segment)
from .multiregion import (to_oriented_segments
                          as multiregion_to_oriented_segments)
from .polygon import (relate_point as relate_point_to_polygon,
                      relate_segment as relate_segment_to_polygon,
                      to_oriented_segments as polygon_to_oriented_segments)
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import to_oriented_segments as region_to_oriented_segments
from .sweep import CompoundSweeper


def relate_point(multipolygon: Multipolygon, point: Point,
                 *,
                 context: Context) -> Relation:
    for polygon in multipolygon:
        relation_with_polygon = relate_point_to_polygon(polygon, point,
                                                        context=context)
        if relation_with_polygon is not Relation.DISJOINT:
            return relation_with_polygon
    return Relation.DISJOINT


def relate_segment(multipolygon: Multipolygon, segment: Segment,
                   *,
                   context: Context) -> Relation:
    do_not_touch = True
    for polygon in multipolygon:
        relation_with_polygon = relate_segment_to_polygon(polygon, segment,
                                                          context=context)
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
                        multisegment: Multisegment,
                        *,
                        context: Context) -> Relation:
    if not (multisegment and multipolygon):
        return Relation.DISJOINT
    multisegment_bounding_box = box.from_iterables(multisegment,
                                                   context=context)
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for polygon in multipolygon:
        border, _ = polygon
        polygon_bounding_box = box.from_iterable(border,
                                                 context=context)
        if not box.disjoint_with(polygon_bounding_box,
                                 multisegment_bounding_box):
            if disjoint:
                disjoint = False
                multipolygon_max_x = polygon_bounding_box.max_x
                sweeper = CompoundSweeper()
                sweeper.register_segments(multisegment,
                                          from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         polygon_bounding_box.max_x)
            sweeper.register_segments(
                    polygon_to_oriented_segments(polygon,
                                                 context=context),
                    from_test=False)
    if disjoint:
        return Relation.DISJOINT
    return process_linear_compound_queue(sweeper,
                                         min(multisegment_bounding_box.max_x,
                                             multipolygon_max_x))


def relate_contour(multipolygon: Multipolygon, contour: Contour,
                   *,
                   context: Context) -> Relation:
    if not multipolygon:
        return Relation.DISJOINT
    contour_bounding_box = box.from_iterable(contour,
                                             context=context)
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for polygon in multipolygon:
        border, _ = polygon
        polygon_bounding_box = box.from_iterable(border,
                                                 context=context)
        if not box.disjoint_with(polygon_bounding_box,
                                 contour_bounding_box):
            if disjoint:
                disjoint = False
                multipolygon_max_x = polygon_bounding_box.max_x
                sweeper = CompoundSweeper()
                sweeper.register_segments(contour_to_segments(contour),
                                          from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         polygon_bounding_box.max_x)
            sweeper.register_segments(
                    polygon_to_oriented_segments(polygon,
                                                 context=context),
                    from_test=False)
    if disjoint:
        return Relation.DISJOINT
    return process_linear_compound_queue(sweeper,
                                         min(contour_bounding_box.max_x,
                                             multipolygon_max_x))


def relate_region(multipolygon: Multipolygon, region: Region,
                  *,
                  context: Context) -> Relation:
    if not multipolygon:
        return Relation.DISJOINT
    region_bounding_box = box.from_iterable(region,
                                            context=context)
    all_disjoint, none_disjoint, multipolygon_max_x, sweeper = (True, True,
                                                                None, None)
    for polygon in multipolygon:
        border, _ = polygon
        polygon_bounding_box = box.from_iterable(border,
                                                 context=context)
        if box.disjoint_with(region_bounding_box,
                             polygon_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                multipolygon_max_x = polygon_bounding_box.max_x
                sweeper = CompoundSweeper()
                sweeper.register_segments(
                        region_to_oriented_segments(region,
                                                    context=context),
                        from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         polygon_bounding_box.max_x)
            sweeper.register_segments(
                    polygon_to_oriented_segments(polygon,
                                                 context=context),
                    from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    relation = process_compound_queue(sweeper, min(multipolygon_max_x,
                                                   region_bounding_box.max_x))
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
                       multiregion: Multiregion,
                       *,
                       context: Context) -> Relation:
    if not (multipolygon and multiregion):
        return Relation.DISJOINT
    multiregion_bounding_box = box.from_iterables(multiregion,
                                                  context=context)
    multipolygon_bounding_box = box.from_iterables(
            _to_borders(multipolygon),
            context=context)
    if box.disjoint_with(multipolygon_bounding_box,
                         multiregion_bounding_box):
        return Relation.DISJOINT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(multipolygon,
                                                   context=context),
                              from_test=False)
    sweeper.register_segments(
            multiregion_to_oriented_segments(multiregion,
                                             context=context),
            from_test=True)
    return process_compound_queue(sweeper,
                                  min(multipolygon_bounding_box.max_x,
                                      multiregion_bounding_box.max_x))


def relate_polygon(multipolygon: Multipolygon, polygon: Polygon,
                   *,
                   context: Context) -> Relation:
    if not multipolygon:
        return Relation.DISJOINT
    border, _ = polygon
    polygon_bounding_box = box.from_iterable(border,
                                             context=context)
    all_disjoint, none_disjoint, multipolygon_max_x, sweeper = (True, True,
                                                                None, None)
    for sub_polygon in multipolygon:
        border, _ = sub_polygon
        sub_polygon_bounding_box = box.from_iterable(border,
                                                     context=context)
        if box.disjoint_with(sub_polygon_bounding_box,
                             polygon_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                multipolygon_max_x = sub_polygon_bounding_box.max_x
                sweeper = CompoundSweeper()
                sweeper.register_segments(
                        polygon_to_oriented_segments(polygon,
                                                     context=context),
                        from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         sub_polygon_bounding_box.max_x)
            sweeper.register_segments(
                    polygon_to_oriented_segments(sub_polygon,
                                                 context=context),
                    from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    relation = process_compound_queue(sweeper, min(multipolygon_max_x,
                                                   polygon_bounding_box.max_x))
    return (relation
            if none_disjoint
            else (Relation.COMPONENT
                  if relation is Relation.EQUAL
                  else (Relation.OVERLAP
                        if relation in (Relation.COVER,
                                        Relation.ENCLOSES,
                                        Relation.COMPOSITE)
                        else relation)))


def relate_multipolygon(goal: Multipolygon, test: Multipolygon,
                        *,
                        context: Context) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    goal_bounding_box = box.from_iterables(_to_borders(goal),
                                           context=context)
    test_bounding_box = box.from_iterables(_to_borders(test),
                                           context=context)
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(goal,
                                                   context=context),
                              from_test=False)
    sweeper.register_segments(to_oriented_segments(test,
                                                   context=context),
                              from_test=True)
    return process_compound_queue(sweeper,
                                  min(goal_bounding_box.max_x,
                                      test_bounding_box.max_x))


def to_oriented_segments(polygons: Iterable[Polygon],
                         *,
                         clockwise: bool = False,
                         context: Context) -> Iterable[Segment]:
    for polygon in polygons:
        yield from polygon_to_oriented_segments(polygon,
                                                clockwise=clockwise,
                                                context=context)


def _to_borders(multipolygon: Multipolygon) -> Iterable[Region]:
    return (border for border, _ in multipolygon)
