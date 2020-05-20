from orient.hints import (Multisegment,
                          Point)
from .relation import Relation
from .segment import relate_point as relate_point_to_segment


def relate_point(multisegment: Multisegment, point: Point) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(segment, point) is Relation.DISJOINT
                   for segment in multisegment)
            else Relation.COMPONENT)
