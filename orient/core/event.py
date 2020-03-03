from reprlib import recursive_repr
from typing import Optional

from reprit.base import generate_repr
from robust.linear import segments_intersection

from orient.hints import (Coordinate,
                          Point,
                          Segment)


class Event:
    __slots__ = ('is_left_endpoint', 'start', 'complement',
                 'from_left_contour', 'below_from_right_contour_in_out')

    def __init__(self,
                 is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['Event'],
                 from_left_contour: bool,
                 below_from_right_contour_in_out: Optional[bool] = None
                 ) -> None:
        self.is_left_endpoint = is_left_endpoint
        self.start = start
        self.complement = complement
        self.from_left_contour = from_left_contour
        self.below_from_right_contour_in_out = below_from_right_contour_in_out

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

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
