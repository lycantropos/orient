from typing import Tuple

from hypothesis import given

from orient.core.region import (boundary_edges,
                                equals)
from orient.hints import (Region,
                          Segment)
from orient.planar import (Relation,
                           point_in_region,
                           segment_in_region)
from tests.utils import (equivalence,
                         implication,
                         to_contour_separators,
                         to_convex_hull)
from . import strategies


@given(strategies.contours_with_segments)
def test_basic(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert isinstance(result, Relation)


@given(strategies.contours_with_segments)
def test_outside(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_region(start, region) is Relation.DISJOINT
                       and point_in_region(end, region) is Relation.DISJOINT)


@given(strategies.contours)
def test_edges(region: Region) -> None:
    assert all(segment_in_region(edge, region) is Relation.COMPONENT
               for edge in boundary_edges(region))


@given(strategies.contours)
def test_contour_separators(region: Region) -> None:
    assert all(segment_in_region(segment, region)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for segment in to_contour_separators(region))


@given(strategies.contours)
def test_convex_contour_criterion(region: Region) -> None:
    assert equivalence(all(segment_in_region(segment, region)
                           is Relation.ENCLOSED
                           for segment in to_contour_separators(region)),
                       equals(region, to_convex_hull(region)))
