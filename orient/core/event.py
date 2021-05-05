from reprlib import recursive_repr
from typing import (Optional,
                    TypeVar)

from ground.hints import Point
from reprit.base import generate_repr

from .enums import (OverlapKind,
                    SegmentsRelation)
from .hints import SegmentEndpoints


class LinearEvent:
    @classmethod
    def from_endpoints(cls, endpoints, from_test: bool) -> 'LinearEvent':
        start, end = endpoints
        if start > end:
            start, end = end, start
        result = cls(start, None, start, True, from_test,
                     SegmentsRelation.DISJOINT)
        result.complement = cls(end, result, end, False, from_test,
                                SegmentsRelation.DISJOINT)
        return result

    __slots__ = ('complement', 'from_test', 'is_left', 'original_start',
                 'relation', 'start')

    def __init__(self,
                 start: Point,
                 complement: Optional['Event'],
                 original_start: Point,
                 is_left: bool,
                 from_test: bool,
                 relation: SegmentsRelation) -> None:
        self.complement, self.original_start, self.start = (
            complement, original_start, start)
        self.is_left = is_left
        self.from_test = from_test
        self.relation = relation

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def from_goal(self) -> bool:
        return not self.from_test

    @property
    def original_end(self) -> Point:
        return self.complement.original_start

    def divide(self, break_point: Point) -> 'LinearEvent':
        tail = self.complement.complement = LinearEvent(
                break_point, self.complement, self.original_start,
                True, self.from_test, self.complement.relation)
        self.complement = LinearEvent(break_point, self, self.original_end,
                                      False, self.from_test, self.relation)
        return tail


class CompoundEvent:
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_test: bool) -> 'CompoundEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        result = cls(start, None, start, True, from_test,
                     SegmentsRelation.DISJOINT, inside_on_left)
        result.complement = cls(end, result, end, False, from_test,
                                SegmentsRelation.DISJOINT, inside_on_left)
        return result

    __slots__ = ('complement', 'from_test', 'interior_to_left', 'is_left',
                 'original_start', 'other_interior_to_left', 'overlap_kind',
                 'relation', 'start')

    def __init__(self,
                 start: Point,
                 complement: Optional['CompoundEvent'],
                 original_start: Point,
                 is_left: bool,
                 from_test: bool,
                 relation: SegmentsRelation,
                 interior_to_left: bool) -> None:
        self.complement, self.original_start, self.start = (
            complement, original_start, start)
        self.is_left = is_left
        self.from_test = from_test
        self.relation = relation
        self.overlap_kind = OverlapKind.NONE
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = False

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def from_goal(self) -> bool:
        return not self.from_test

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
    def original_end(self) -> Point:
        return self.complement.original_start

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    def divide(self, break_point: Point) -> 'CompoundEvent':
        tail = self.complement.complement = CompoundEvent(
                break_point, self.complement, self.original_start, True,
                self.from_test, self.complement.relation,
                self.interior_to_left)
        self.complement = CompoundEvent(
                break_point, self, self.original_end, False, self.from_test,
                self.relation, self.interior_to_left)
        return tail


Event = TypeVar('Event', LinearEvent, CompoundEvent)
