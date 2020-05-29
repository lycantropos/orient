from orient.hints import (Multipolygon,
                          Point)
from .polygon import relate_point as relate_point_to_polygon
from .relation import Relation


def relate_point(multipolygon: Multipolygon, point: Point) -> Relation:
    for polygon in multipolygon:
        relation_with_polygon = relate_point_to_polygon(polygon, point)
        if relation_with_polygon is not Relation.DISJOINT:
            return relation_with_polygon
    return Relation.DISJOINT
