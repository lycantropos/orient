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


class LinearEvent:
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
class OverlapTransition(IntEnum):
    NONE = 0
    SAME = 1
    DIFFERENT = 2


class CompoundEvent(LinearEvent):
    __slots__ = 'overlap_transition', 'in_out', 'other_in_out'

    def __init__(self,
                 is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['CompoundEvent'],
                 from_test: bool,
                 relationship: SegmentsRelationship) -> None:
        super().__init__(is_left_endpoint, start, complement, from_test,
                         relationship)
        self.overlap_transition = OverlapTransition.NONE
        self.in_out = None
        self.other_in_out = None

    @property
    def common_boundary(self) -> bool:
        """
        Checks if the segment lies on the boundary of the components
        which intersect in region.
        """
        return self.overlap_transition is OverlapTransition.SAME

    @property
    def contours_overlap(self) -> bool:
        """
        Checks if the segment is a separate component of the intersection.
        """
        return self.overlap_transition is OverlapTransition.DIFFERENT

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (not self.other_in_out
                and self.overlap_transition is OverlapTransition.NONE)

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches
        or disjoint with the region of the intersection.
        """
        return (self.other_in_out
                and self.overlap_transition is OverlapTransition.NONE)


Event = TypeVar('Event', LinearEvent, CompoundEvent)
