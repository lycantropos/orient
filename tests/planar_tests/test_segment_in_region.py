from typing import Tuple

from ground.hints import Segment
from hypothesis import given

from orient.hints import Region
from orient.planar import (Relation,
                           point_in_region,
                           segment_in_contour,
                           segment_in_region)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         are_regions_equal,
                         equivalence,
                         implication,
                         region_rotations,
                         reverse_contour,
                         reverse_segment,
                         to_contour_separators,
                         to_region_convex_hull,
                         to_region_edges)
from . import strategies


@given(strategies.contours_with_segments)
def test_basic(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert all(segment_in_region(edge, region) is Relation.COMPONENT
               for edge in to_region_edges(region))


@given(strategies.contours)
def test_separators(region: Region) -> None:
    assert all(segment_in_region(segment, region)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for segment in to_contour_separators(region))


@given(strategies.contours)
def test_convex_region(region: Region) -> None:
    assert implication(are_regions_equal(region,
                                         to_region_convex_hull(region)),
                       all(segment_in_region(segment, region)
                           is Relation.ENCLOSED
                           for segment in to_contour_separators(region)))


@given(strategies.contours_with_segments)
def test_reversals(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert result is segment_in_region(reverse_segment(segment), region)
    assert result is segment_in_region(segment, reverse_contour(region))


@given(strategies.contours_with_segments)
def test_rotations(region_with_segment: Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    assert all(result is segment_in_region(segment, rotated)
               for rotated in region_rotations(region))


@given(strategies.contours_with_segments)
def test_connection_with_point_in_region(region_with_segment
                                         : Tuple[Region, Segment]) -> None:
    region, segment = region_with_segment

    result = segment_in_region(segment, region)

    start_relation, end_relation = (point_in_region(segment.start, region),
                                    point_in_region(segment.end, region))
    assert implication(result is Relation.DISJOINT,
                       start_relation is end_relation is Relation.DISJOINT)
    assert implication(result is Relation.COMPONENT,
                       start_relation is end_relation is Relation.COMPONENT)
    assert implication(result is Relation.WITHIN,
                       start_relation is end_relation is Relation.WITHIN)
    assert implication(start_relation is Relation.DISJOINT
                       and end_relation is Relation.WITHIN
                       or start_relation is Relation.WITHIN
                       and end_relation is Relation.DISJOINT,
                       result is Relation.CROSS)


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
