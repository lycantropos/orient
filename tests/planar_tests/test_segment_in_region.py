from typing import Tuple

from hypothesis import given

from orient.core.region import (boundary_edges,
                                equal)
from orient.hints import (Region,
                          Segment)
from orient.planar import (Relation,
                           point_in_region,
                           segment_in_contour,
                           segment_in_region)
from tests.utils import (equivalence,
                         implication,
                         reverse_contour,
                         reverse_segment,
                         rotations,
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
                       equal(region, to_convex_hull(region)))


@given(strategies.contours_with_segments)
def test_reversed_segment(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert result is segment_in_region(reverse_segment(segment), region)


@given(strategies.contours_with_segments)
def test_reversed_region(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert result is segment_in_region(segment, reverse_contour(region))


@given(strategies.contours_with_segments)
def test_rotations(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert all(result is segment_in_region(segment, rotated)
               for rotated in rotations(region))


@given(strategies.contours_with_segments)
def test_connection_with_segment_in_contour(region_with_segment
                                            : Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    relation_with_contour = segment_in_contour(segment, region)
    assert implication(result is Relation.DISJOINT,
                       relation_with_contour is Relation.DISJOINT)
    assert implication(result is Relation.TOUCH,
                       relation_with_contour is Relation.TOUCH
                       or relation_with_contour is Relation.OVERLAP)
    assert equivalence(result is Relation.CROSS,
                       relation_with_contour is Relation.CROSS)
    assert equivalence(result is Relation.COMPONENT,
                       relation_with_contour is Relation.COMPONENT)
    assert implication(result is Relation.ENCLOSED,
                       relation_with_contour is Relation.TOUCH
                       or relation_with_contour is Relation.OVERLAP)
    assert implication(result is Relation.WITHIN,
                       relation_with_contour is Relation.DISJOINT)
    assert implication(relation_with_contour is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       or result is Relation.WITHIN)
    assert implication(relation_with_contour is Relation.TOUCH,
                       result is Relation.TOUCH
                       or result is Relation.ENCLOSED)
    assert implication(relation_with_contour is Relation.OVERLAP,
                       result is Relation.TOUCH
                       or result is Relation.ENCLOSED)
