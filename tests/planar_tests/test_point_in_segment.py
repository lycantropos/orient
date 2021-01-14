from typing import Tuple

from ground.base import Orientation
from ground.hints import (Point,
                          Segment)
from hypothesis import given

from orient.planar import (Relation,
                           point_in_segment)
from tests.utils import (PRIMITIVE_LINEAR_RELATIONS,
                         implication,
                         orientation,
                         reverse_point_coordinates,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.segments_with_points)
def test_basic(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    result = point_in_segment(point, segment)

    assert isinstance(result, Relation)
    assert result in PRIMITIVE_LINEAR_RELATIONS


@given(strategies.segments)
def test_self(segment: Segment) -> None:
    assert point_in_segment(segment.start, segment) is Relation.COMPONENT
    assert point_in_segment(segment.end, segment) is Relation.COMPONENT


@given(strategies.segments_with_points)
def test_orientation(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    assert implication(point_in_segment(point, segment) is Relation.COMPONENT,
                       orientation(segment.start, segment.end, point)
                       is Orientation.COLLINEAR)


@given(strategies.segments_with_points)
def test_reversals(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    result = point_in_segment(point, segment)

    assert result is point_in_segment(point, reverse_segment(segment))
    assert result is point_in_segment(reverse_point_coordinates(point),
                                      reverse_segment_coordinates(segment))
