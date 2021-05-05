from typing import Iterable

from ground.base import (Context,
                         Relation)
from ground.hints import (Contour,
                          Multipolygon,
                          Multisegment,
                          Point,
                          Polygon,
                          Segment)

from . import box
from .contour import to_edges_endpoints as contour_to_edges_endpoints
from .events_queue import CompoundEventsQueue
from .hints import (Multiregion,
                    Region,
                    SegmentEndpoints)
from .multiregion import (to_oriented_edges_endpoints
                          as multiregion_to_oriented_segments)
from .multisegment import to_segments_endpoints
from .polygon import (relate_point as relate_point_to_polygon,
                      to_oriented_edges_endpoints
                      as polygon_to_oriented_segments)
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import to_oriented_segments as region_to_oriented_segments


def relate_point(multipolygon: Multipolygon,
                 point: Point,
                 context: Context) -> Relation:
    for polygon in multipolygon.polygons:
        relation_with_polygon = relate_point_to_polygon(polygon, point,
                                                        context)
        if relation_with_polygon is not Relation.DISJOINT:
            return relation_with_polygon
    return Relation.DISJOINT


def relate_segment(multipolygon: Multipolygon,
                   segment: Segment,
                   context: Context) -> Relation:
    return relate_multisegment(multipolygon,
                               context.multisegment_cls([segment]), context)


def relate_multisegment(multipolygon: Multipolygon,
                        multisegment: Multisegment,
                        context: Context) -> Relation:
    multisegment_bounding_box = context.segments_box(multisegment.segments)
    disjoint, multipolygon_max_x, events_queue = True, None, None
    for polygon in multipolygon.polygons:
        polygon_bounding_box = context.polygon_box(polygon)
        if not box.disjoint_with(polygon_bounding_box,
                                 multisegment_bounding_box):
            if disjoint:
                disjoint = False
                multipolygon_max_x = polygon_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(to_segments_endpoints(multisegment),
                                      from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         polygon_bounding_box.max_x)
            events_queue.register(polygon_to_oriented_segments(polygon,
                                                               context),
                                  from_test=False)
    return (Relation.DISJOINT
            if disjoint
            else
            process_linear_compound_queue(events_queue,
                                          min(multisegment_bounding_box.max_x,
                                              multipolygon_max_x)))


def relate_contour(multipolygon: Multipolygon,
                   contour: Contour,
                   context: Context) -> Relation:
    contour_bounding_box = context.contour_box(contour)
    disjoint, multipolygon_max_x, events_queue = True, None, None
    for polygon in multipolygon.polygons:
        polygon_bounding_box = context.polygon_box(polygon)
        if not box.disjoint_with(polygon_bounding_box, contour_bounding_box):
            if disjoint:
                disjoint = False
                multipolygon_max_x = polygon_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(contour_to_edges_endpoints(contour),
                                      from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         polygon_bounding_box.max_x)
            events_queue.register(polygon_to_oriented_segments(polygon,
                                                               context),
                                  from_test=False)
    return (Relation.DISJOINT
            if disjoint
            else process_linear_compound_queue(events_queue,
                                               min(contour_bounding_box.max_x,
                                                   multipolygon_max_x)))


def relate_region(multipolygon: Multipolygon,
                  region: Region,
                  context: Context) -> Relation:
    region_bounding_box = context.contour_box(region)
    all_disjoint, none_disjoint, multipolygon_max_x, events_queue = (
        True, True, None, None)
    for polygon in multipolygon.polygons:
        polygon_bounding_box = context.polygon_box(polygon)
        if box.disjoint_with(region_bounding_box, polygon_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                multipolygon_max_x = polygon_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(region_to_oriented_segments(region,
                                                                  context),
                                      from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         polygon_bounding_box.max_x)
            events_queue.register(polygon_to_oriented_segments(polygon,
                                                               context),
                                  from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    relation = process_compound_queue(events_queue,
                                      min(multipolygon_max_x,
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
                       context: Context) -> Relation:
    multiregion_bounding_box = context.contours_box(multiregion)
    multipolygon_bounding_box = context.polygons_box(multipolygon.polygons)
    if box.disjoint_with(multipolygon_bounding_box, multiregion_bounding_box):
        return Relation.DISJOINT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(multipolygon, context),
                          from_test=False)
    events_queue.register(multiregion_to_oriented_segments(multiregion,
                                                           context),
                          from_test=True)
    return process_compound_queue(events_queue,
                                  min(multipolygon_bounding_box.max_x,
                                      multiregion_bounding_box.max_x))


def relate_polygon(multipolygon: Multipolygon,
                   polygon: Polygon,
                   context: Context) -> Relation:
    polygon_bounding_box = context.polygon_box(polygon)
    all_disjoint, none_disjoint, multipolygon_max_x, events_queue = (
        True, True, None, None)
    for sub_polygon in multipolygon.polygons:
        sub_polygon_bounding_box = context.polygon_box(sub_polygon)
        if box.disjoint_with(sub_polygon_bounding_box, polygon_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                multipolygon_max_x = sub_polygon_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(polygon_to_oriented_segments(polygon,
                                                                   context),
                                      from_test=True)
            else:
                multipolygon_max_x = max(multipolygon_max_x,
                                         sub_polygon_bounding_box.max_x)
            events_queue.register(polygon_to_oriented_segments(sub_polygon,
                                                               context),
                                  from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    relation = process_compound_queue(events_queue,
                                      min(multipolygon_max_x,
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


def relate_multipolygon(goal: Multipolygon,
                        test: Multipolygon,
                        context: Context) -> Relation:
    goal_bounding_box = context.polygons_box(goal.polygons)
    test_bounding_box = context.polygons_box(test.polygons)
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(goal, context),
                          from_test=False)
    events_queue.register(to_oriented_segments(test, context),
                          from_test=True)
    return process_compound_queue(events_queue,
                                  min(goal_bounding_box.max_x,
                                      test_bounding_box.max_x))


def to_oriented_segments(multipolygon: Multipolygon,
                         context: Context,
                         clockwise: bool = False
                         ) -> Iterable[SegmentEndpoints]:
    for polygon in multipolygon.polygons:
        yield from polygon_to_oriented_segments(polygon, context, clockwise)
