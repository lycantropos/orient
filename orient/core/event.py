from enum import (IntEnum,
                  unique)
from reprlib import recursive_repr
from typing import (Optional,
                    TypeVar)

from reprit.base import generate_repr
from robust.linear import SegmentsRelationship

from orient.hints import (Point,
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

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def set_both_relationships(self, relationship: SegmentsRelationship
                               ) -> None:
        self.relationship = self.complement.relationship = relationship


@unique
class OverlapKind(IntEnum):
    NONE = 0
    SAME_ORIENTATION = 1
    DIFFERENT_ORIENTATION = 2


class CompoundEvent(LinearEvent):
    __slots__ = 'overlap_kind', 'interior_to_left', 'other_interior_to_left'

    def __init__(self,
                 is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['CompoundEvent'],
                 from_test: bool,
                 relationship: SegmentsRelationship,
                 interior_to_left: bool) -> None:
        super().__init__(is_left_endpoint, start, complement, from_test,
                         relationship)
        self.overlap_kind = OverlapKind.NONE
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = False

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def is_common_polyline_component(self) -> bool:
        """
        Checks if the segment is a component of intersection's polyline.
        """
        return self.overlap_kind is OverlapKind.DIFFERENT_ORIENTATION

    @property
    def is_common_region_boundary(self) -> bool:
        """
        Checks if the segment is a boundary of intersection's region.
        """
        return self.overlap_kind is OverlapKind.SAME_ORIENTATION

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)


Event = TypeVar('Event', LinearEvent, CompoundEvent)
