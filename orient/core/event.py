from enum import (IntEnum,
                  unique)
from reprlib import recursive_repr
from typing import (Optional,
                    TypeVar)

from reprit.base import generate_repr
from robust.linear import (SegmentsRelationship,
                           segments_intersection)

from orient.hints import (Coordinate,
                          Point,
                          Segment)


class OpenEvent:
    __slots__ = ('is_left_endpoint', 'start', 'complement', 'from_test',
                 'relationship')

    def __init__(self,
                 is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['Event'],
                 from_test: bool,
                 relationship: SegmentsRelationship) -> None:
        self.is_left_endpoint = is_left_endpoint
        self.start = start
        self.complement = complement
        self.from_test = from_test
        self.relationship = relationship

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_goal(self) -> bool:
        return not self.from_test

    @property
    def end(self) -> Point:
        return self.complement.start

    def set_both_relationships(self, relationship: SegmentsRelationship
                               ) -> None:
        self.relationship = self.complement.relationship = relationship

    @property
    def is_vertical(self) -> bool:
        start_x, _ = self.start
        end_x, _ = self.end
        return start_x == end_x

    @property
    def is_horizontal(self) -> bool:
        _, start_y = self.start
        _, end_y = self.end
        return start_y == end_y

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def y_at(self, x: Coordinate) -> Coordinate:
        if self.is_vertical or self.is_horizontal:
            _, start_y = self.start
            return start_y
        else:
            start_x, start_y = self.start
            if x == start_x:
                return start_y
            end_x, end_y = self.end
            if x == end_x:
                return end_y
            _, result = segments_intersection(self.segment,
                                              ((x, start_y), (x, end_y)))
            return result


@unique
class EdgeKind(IntEnum):
    NORMAL = 0
    NON_CONTRIBUTING = 1
    SAME_TRANSITION = 2
    DIFFERENT_TRANSITION = 3


class ClosedEvent(OpenEvent):
    __slots__ = 'edge_kind', 'in_out', 'other_in_out'

    def __init__(self, is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['ClosedEvent'],
                 from_test: bool,
                 relationship: SegmentsRelationship) -> None:
        super().__init__(is_left_endpoint, start, complement, from_test,
                         relationship)
        self.edge_kind = EdgeKind.NORMAL
        self.in_out = None
        self.other_in_out = None

    @property
    def in_intersection(self) -> bool:
        return (self.edge_kind is EdgeKind.NORMAL and not self.other_in_out
                or self.edge_kind is EdgeKind.SAME_TRANSITION)

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (self.in_intersection
                and (self.relationship is SegmentsRelationship.NONE
                     or self.relationship is SegmentsRelationship.TOUCH))

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches
        or disjoint with the region of the intersection.
        """
        return (not self.in_intersection
                and self.relationship is not SegmentsRelationship.OVERLAP)


Event = TypeVar('Event', OpenEvent, ClosedEvent)
