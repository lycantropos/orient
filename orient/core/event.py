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
class OverlapOrientation(IntEnum):
    NONE = 0
    SAME = 1
    DIFFERENT = 2


class CompoundEvent(LinearEvent):
    __slots__ = 'overlap_orientation', 'inside_on_left', 'other_inside_on_left'

    def __init__(self,
                 is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['CompoundEvent'],
                 from_test: bool,
                 relationship: SegmentsRelationship,
                 inside_on_left: bool) -> None:
        super().__init__(is_left_endpoint, start, complement, from_test,
                         relationship)
        self.overlap_orientation = OverlapOrientation.NONE
        self.inside_on_left = inside_on_left
        self.other_inside_on_left = False

    @property
    def common_boundary(self) -> bool:
        """
        Checks if the segment lies on the boundary of the components
        which intersect in region.
        """
        return self.overlap_orientation is OverlapOrientation.SAME

    @property
    def contours_overlap(self) -> bool:
        """
        Checks if the segment is a separate component of the intersection.
        """
        return self.overlap_orientation is OverlapOrientation.DIFFERENT

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (self.other_inside_on_left
                and self.overlap_orientation is OverlapOrientation.NONE)

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches
        or disjoint with the region of the intersection.
        """
        return (not self.other_inside_on_left
                and self.overlap_orientation is OverlapOrientation.NONE)


Event = TypeVar('Event', LinearEvent, CompoundEvent)
