from typing import Tuple

from hypothesis import given

from orient.core.contour import to_segments
from orient.hints import (Contour,
                          Segment)
from orient.planar import (PointLocation,
                           SegmentLocation,
                           point_in_contour,
                           segment_in_contour)
from tests.utils import (are_contours_similar,
                         equivalence,
                         implication,
                         to_convex_hull,
                         to_non_edge_rays)
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
                       is PointLocation.OUTSIDE
                       and point_in_contour(end, contour)
                       is PointLocation.OUTSIDE)


@given(strategies.contours)
def test_edges(contour: Contour) -> None:
    assert all(segment_in_contour(edge, contour) is SegmentLocation.BOUNDARY
               for edge in to_segments(contour))


@given(strategies.contours)
def test_convex_contour_criterion(contour: Contour) -> None:
    assert equivalence(all(segment_in_contour(ray, contour)
                           is SegmentLocation.INSIDE
                           for ray in to_non_edge_rays(contour)),
                       are_contours_similar(contour, to_convex_hull(contour)))
