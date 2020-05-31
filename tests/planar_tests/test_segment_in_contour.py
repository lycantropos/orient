from typing import Tuple

from hypothesis import given

from orient.core.contour import (equal,
                                 to_segments)
from orient.hints import (Contour,
                          Segment)
from orient.planar import (Relation,
                           point_in_contour,
                           segment_in_contour)
from tests.utils import (LINEAR_RELATIONS,
                         implication,
                         reverse_contour,
                         reverse_segment,
                         rotations,
                         to_contour_separators,
                         to_convex_hull)
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
               for edge in to_segments(contour))


@given(strategies.contours)
def test_separators(contour: Contour) -> None:
    assert all(segment_in_contour(segment, contour) in (Relation.TOUCH,
                                                        Relation.CROSS,
                                                        Relation.OVERLAP)
               for segment in to_contour_separators(contour))


@given(strategies.contours)
def test_convex_contour(contour: Contour) -> None:
    assert implication(equal(contour, to_convex_hull(contour)),
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
               for rotated in rotations(contour))


@given(strategies.contours_with_segments)
def test_connection_with_point_in_contour(contour_with_segment
                                          : Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_contour(start, contour) is Relation.DISJOINT
                       and point_in_contour(end, contour) is Relation.DISJOINT)
