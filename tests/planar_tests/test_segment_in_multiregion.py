from typing import Tuple

from ground.base import Relation
from ground.hints import Segment
from hypothesis import given

from orient.hints import Multiregion
from orient.planar import (point_in_multiregion,
                           segment_in_multiregion,
                           segment_in_region)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_multiregion_regions,
                         reverse_segment,
                         reverse_segment_coordinates,
                         sequence_rotations)
from . import strategies


@given(strategies.multiregions_with_segments)
def test_basic(multiregion_with_segment: Tuple[Multiregion, Segment]) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.multiregions_with_segments)
def test_step(multiregion_with_region: Tuple[Multiregion, Segment]) -> None:
    multiregion, segment = multiregion_with_region
    first_region, *rest_multiregion = multiregion

    result = segment_in_multiregion(segment, rest_multiregion)
    next_result = segment_in_multiregion(segment, multiregion)

    relation_with_first_region = segment_in_region(segment, first_region)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       and relation_with_first_region is Relation.DISJOINT)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_region is Relation.WITHIN)
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_region is Relation.COMPONENT)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_region is Relation.CROSS)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_region is Relation.TOUCH)


@given(strategies.multiregions_with_segments)
def test_reversals(multiregion_with_segment: Tuple[Multiregion, Segment]
                   ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert result is segment_in_multiregion(reverse_segment(segment),
                                            multiregion)
    assert result is segment_in_multiregion(segment,
                                            reverse_multiregion(multiregion))
    assert result is segment_in_multiregion(
            segment, reverse_multiregion_regions(multiregion))
    assert result is segment_in_multiregion(
            reverse_segment_coordinates(segment),
            reverse_multiregion_coordinates(multiregion))


@given(strategies.multiregions_with_segments)
def test_rotations(multiregion_with_segment: Tuple[Multiregion, Segment]
                   ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert all(result is segment_in_multiregion(segment, rotated)
               for rotated in sequence_rotations(multiregion))


@given(strategies.multiregions_with_segments)
def test_connection_with_point_in_multiregion(multiregion_with_segment
                                              : Tuple[Multiregion, Segment]
                                              ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert implication(result is Relation.DISJOINT,
                       point_in_multiregion(segment.start, multiregion)
                       is point_in_multiregion(segment.end, multiregion)
                       is Relation.DISJOINT)
