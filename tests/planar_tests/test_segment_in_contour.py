from typing import Tuple

from hypothesis import given

from orient.core.contour import (edges,
                                 equal)
from orient.hints import (Contour,
                          Segment)
from orient.planar import (Relation,
                           point_in_contour,
                           segment_in_contour)
from tests.utils import (implication,
                         to_contour_separators,
                         to_convex_hull)
from . import strategies


@given(strategies.contours_with_segments)
def test_basic(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    assert isinstance(result, Relation)


@given(strategies.contours_with_segments)
def test_outside(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_contour(start, contour) is Relation.DISJOINT
                       and point_in_contour(end, contour) is Relation.DISJOINT)


@given(strategies.contours)
def test_edges(contour: Contour) -> None:
    assert all(segment_in_contour(edge, contour) is Relation.COMPONENT
               for edge in edges(contour))


@given(strategies.contours)
def test_contour_separators(contour: Contour) -> None:
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
