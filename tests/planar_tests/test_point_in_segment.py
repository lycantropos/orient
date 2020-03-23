from typing import Tuple

from hypothesis import given
from robust.angular import (Orientation,
                            orientation)

from orient.hints import (Point,
                          Segment)
from orient.planar import (PointLocation,
                           point_in_segment)
from tests.utils import (implication,
                         reverse_point_coordinates,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.segments_with_points)
def test_basic(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    result = point_in_segment(point, segment)

    assert isinstance(result, PointLocation)


@given(strategies.segments)
def test_endpoints(segment: Segment) -> None:
    start, end = segment

    assert point_in_segment(start, segment) is PointLocation.BOUNDARY
    assert point_in_segment(end, segment) is PointLocation.BOUNDARY


@given(strategies.segments_with_points)
def test_orientation(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    start, end = segment
    assert implication(point_in_segment(point, segment)
                       is not PointLocation.EXTERNAL,
                       orientation(end, start, point) is Orientation.COLLINEAR)


@given(strategies.segments_with_points)
def test_reversed(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    assert (point_in_segment(point, segment)
            is point_in_segment(point, reverse_segment(segment)))


@given(strategies.segments_with_points)
def test_reversed_coordinates(segment_with_point: Tuple[Segment, Point]
                              ) -> None:
    segment, point = segment_with_point

    assert (point_in_segment(point, segment)
            is point_in_segment(reverse_point_coordinates(point),
                                reverse_segment_coordinates(segment)))
