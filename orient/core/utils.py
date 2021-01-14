from enum import IntEnum
from itertools import chain

from ground.base import (Orientation,
                         Relation,
                         get_context)

Orientation = Orientation


def orientation(vertex, first, second):
    context = get_context()
    return context.angle_orientation(vertex, first, second)


def segments_intersection(first, second):
    first_start, first_end = first
    second_start, second_end = second
    context = get_context()
    return context.segments_intersection(first_start, first_end, second_start,
                                         second_end)


class SegmentsRelationship(IntEnum):
    NONE = 0
    TOUCH = 1
    CROSS = 2
    OVERLAP = 3


def segments_relationship(first, second):
    first_start, first_end = first
    second_start, second_end = second
    context = get_context()
    result = context.segments_relation(first_start, first_end, second_start,
                                       second_end)
    return (SegmentsRelationship.NONE if result is Relation.DISJOINT
            else (SegmentsRelationship.TOUCH if result is Relation.TOUCH
                  else (SegmentsRelationship.CROSS if result is Relation.CROSS
                        else SegmentsRelationship.OVERLAP)))


def signed_length(first_start, first_end, second_start, second_end):
    context = get_context()
    return context.dot_product(first_start, first_end, second_start,
                               second_end)


flatten = chain.from_iterable
