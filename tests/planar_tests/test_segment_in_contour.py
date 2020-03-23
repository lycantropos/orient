from typing import Tuple

from hypothesis import given

from orient.core.contour import edges
from orient.hints import (Contour,
                          Segment)
from orient.planar import (PointLocation,
                           SegmentLocation,
                           point_in_contour,
                           segment_in_contour)
from tests.utils import (are_contours_similar,
                         equivalence,
                         implication,
                         to_contour_separators,
                         to_convex_hull)
from . import strategies


@given(strategies.contours_with_segments)
def test_basic(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    assert isinstance(result, SegmentLocation)


@given(strategies.contours_with_segments)
def test_outside(contour_with_segment: Tuple[Contour, Segment]) -> None:
    contour, segment = contour_with_segment

    result = segment_in_contour(segment, contour)

    start, end = segment
    assert implication(result is SegmentLocation.EXTERNAL,
                       point_in_contour(start, contour)
                       is PointLocation.EXTERNAL
                       and point_in_contour(end, contour)
                       is PointLocation.EXTERNAL)


@given(strategies.contours)
def test_edges(contour: Contour) -> None:
    assert all(segment_in_contour(edge, contour) is SegmentLocation.BOUNDARY
               for edge in edges(contour))


@given(strategies.contours)
def test_contour_separators(contour: Contour) -> None:
    assert all(segment_in_contour(segment, contour)
               in (SegmentLocation.TOUCH,
                   SegmentLocation.CROSS,
                   SegmentLocation.ENCLOSED)
               for segment in to_contour_separators(contour))


@given(strategies.contours)
def test_convex_contour_criterion(contour: Contour) -> None:
    assert equivalence(all(segment_in_contour(segment, contour)
                           is SegmentLocation.ENCLOSED
                           for segment in to_contour_separators(contour)),
                       are_contours_similar(contour, to_convex_hull(contour)))
