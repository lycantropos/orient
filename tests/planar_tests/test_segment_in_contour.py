from typing import Tuple

from ground.base import Relation
from ground.hints import (Contour,
                          Segment)
from hypothesis import given

from orient.planar import (point_in_contour,
                           segment_in_contour)
from tests.utils import (LINEAR_RELATIONS,
                         are_contours_equal,
                         contour_rotations,
                         implication,
                         reverse_contour,
                         reverse_segment,
                         to_contour_convex_hull,
                         to_contour_edges,
                         to_contour_separators)
from . import strategies


@given(strategies.contours_with_segments)
def test_basic(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    assert isinstance(result, Relation)
    assert result in LINEAR_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert all(segment_in_contour(edge, contour) is Relation.COMPONENT
               for edge in to_contour_edges(contour))


@given(strategies.contours)
def test_separators(contour: Contour) -> None:
    assert all(segment_in_contour(segment, contour) in (Relation.TOUCH,
                                                        Relation.CROSS,
                                                        Relation.OVERLAP)
               for segment in to_contour_separators(contour))


@given(strategies.contours)
def test_convex_contour(contour: Contour) -> None:
    assert implication(are_contours_equal(contour,
                                          to_contour_convex_hull(contour)),
                       all(segment_in_contour(segment, contour)
                           is Relation.TOUCH
                           for segment in to_contour_separators(contour)))


@given(strategies.contours_with_segments)
def test_reversals(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    assert result is segment_in_contour(reverse_segment(segment), contour)
    assert result is segment_in_contour(segment, reverse_contour(contour))


@given(strategies.contours_with_segments)
def test_rotations(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    assert all(result is segment_in_contour(segment, rotated)
               for rotated in contour_rotations(contour))


@given(strategies.contours_with_segments)
def test_connection_with_point_in_contour(contour_with_segment
                                          : Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    assert implication(result is Relation.DISJOINT,
                       point_in_contour(segment.start, contour)
                       is point_in_contour(segment.end, contour)
                       is Relation.DISJOINT)
