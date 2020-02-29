from typing import Tuple

from hypothesis import given

from orient.core.angular import (Orientation,
                                 to_orientation)
from orient.hints import (Point,
                          Segment)
from orient.planar import point_in_segment
from tests.utils import implication
from . import strategies


@given(strategies.segments_with_points)
def test_orientation(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    result = point_in_segment(point, segment)

    assert isinstance(result, bool)


@given(strategies.segments)
def test_endpoints(segment: Segment) -> None:
    start, end = segment

    assert point_in_segment(start, segment)
    assert point_in_segment(end, segment)


@given(strategies.segments_with_points)
def test_orientation(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    start, end = segment
    assert implication(point_in_segment(point, segment),
                       to_orientation(end, start, point)
                       is Orientation.COLLINEAR)
