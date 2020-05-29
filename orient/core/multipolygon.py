from orient.hints import (Multipolygon,
                          Multisegment,
                          Point,
                          Segment)
from . import bounding_box
from .multiregion import to_segments as multiregion_to_segments
from .polygon import (relate_point as relate_point_to_polygon,
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
    multisegment_bounding_box = bounding_box.from_points(flatten(multisegment))
    disjoint, multipolygon_max_x, sweeper = True, None, None
    for border, holes in multipolygon:
        polygon_bounding_box = bounding_box.from_points(border)
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
