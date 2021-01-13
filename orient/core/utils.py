from enum import IntEnum
from itertools import chain

from ground.base import (Orientation,
                         Relation,
                         get_context)

Orientation = Orientation


def orientation(vertex, first, second):
    context = get_context()
    point_cls = context.point_cls
    return context.angle_orientation(point_cls(*vertex), point_cls(*first),
                                     point_cls(*second))


def segments_intersection(first, second):
    first_start, first_end = first
    second_start, second_end = second
    context = get_context()
    point_cls = context.point_cls
    result = context.segments_intersection(point_cls(*first_start),
                                           point_cls(*first_end),
                                           point_cls(*second_start),
                                           point_cls(*second_end))
    return result.x, result.y


class SegmentsRelationship(IntEnum):
    NONE = 0
    TOUCH = 1
    CROSS = 2
    OVERLAP = 3


def segments_relationship(first, second):
    first_start, first_end = first
    second_start, second_end = second
    context = get_context()
    point_cls = context.point_cls
    result = context.segments_relation(point_cls(*first_start),
                                       point_cls(*first_end),
                                       point_cls(*second_start),
                                       point_cls(*second_end))
    return (SegmentsRelationship.NONE if result is Relation.DISJOINT
            else (SegmentsRelationship.TOUCH if result is Relation.TOUCH
                  else (SegmentsRelationship.CROSS if result is Relation.CROSS
                        else SegmentsRelationship.OVERLAP)))


def signed_length(first_start, first_end, second_start, second_end):
    context = get_context()
    point_cls = context.point_cls
    return context.dot_product(point_cls(*first_start), point_cls(*first_end),
                               point_cls(*second_start),
                               point_cls(*second_end))


flatten = chain.from_iterable
