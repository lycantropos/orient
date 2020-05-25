from typing import Tuple

from hypothesis import given

from orient.core.region import to_segments
from orient.hints import (Multisegment,
                          Region)
from orient.planar import (Relation,
                           multisegment_in_contour,
                           multisegment_in_region,
                           segment_in_region)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_multisegment,
                         rotations)
from . import strategies


@given(strategies.contours_with_multisegments)
def test_basic(region_with_multisegment: Tuple[Region, Multisegment]) -> None:
    region, multisegment = region_with_multisegment

    result = multisegment_in_region(multisegment, region)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.contours)
def test_edges(region: Region) -> None:
    assert multisegment_in_region(list(to_segments(region)),
                                  region) is Relation.COMPONENT


@given(strategies.contours_with_empty_multisegments)
def test_base(region_with_multisegment: Tuple[Region, Multisegment]) -> None:
    region, multisegment = region_with_multisegment

    result = multisegment_in_region(multisegment, region)

    assert result is Relation.DISJOINT


@given(strategies.contours_with_non_empty_multisegments)
def test_step(region_with_multisegment: Tuple[Region, Multisegment]) -> None:
    region, multisegment = region_with_multisegment
    first_segment, *rest_multisegment = multisegment

    result = multisegment_in_region(rest_multisegment, region)
    next_result = multisegment_in_region(multisegment, region)

    relation_with_first_segment = segment_in_region(first_segment, region)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_segment
                       is Relation.DISJOINT)
    assert implication(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and relation_with_first_segment is not Relation.CROSS
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH)
    assert implication(result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_segment is Relation.DISJOINT,
                       next_result is Relation.TOUCH)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_segment is Relation.CROSS
                       or (bool(rest_multisegment)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_segment is Relation.ENCLOSED
                            or relation_with_first_segment is Relation.WITHIN)
                       or (result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       (not rest_multisegment or result is Relation.COMPONENT)
                       and relation_with_first_segment is Relation.COMPONENT)
    assert equivalence(next_result is Relation.ENCLOSED,
                       not rest_multisegment
                       and relation_with_first_segment is Relation.ENCLOSED
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED)
                       and (relation_with_first_segment is Relation.ENCLOSED
                            or relation_with_first_segment is Relation.WITHIN)
                       or (result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and relation_with_first_segment is Relation.COMPONENT
                       or result is Relation.WITHIN
                       and relation_with_first_segment is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_multisegment or result is Relation.WITHIN)
                       and relation_with_first_segment is Relation.WITHIN)


@given(strategies.contours_with_multisegments)
def test_connection_with_multisegment_in_contour(region_with_multisegment
                                                 : Tuple[Region, Multisegment]
                                                 ) -> None:
    region, multisegment = region_with_multisegment

    result = multisegment_in_region(multisegment, region)

    relation_with_contour = multisegment_in_contour(multisegment, region)
    assert implication(result is Relation.DISJOINT,
                       relation_with_contour is Relation.DISJOINT)
    assert implication(result is Relation.TOUCH,
                       relation_with_contour is Relation.TOUCH
                       or relation_with_contour is Relation.OVERLAP)
    assert implication(result is Relation.CROSS,
                       relation_with_contour is not Relation.EQUAL
                       or relation_with_contour is not Relation.COMPONENT)
    assert implication(relation_with_contour is Relation.CROSS,
                       result is Relation.CROSS)
    assert equivalence(result is Relation.COMPONENT,
                       relation_with_contour is Relation.COMPONENT)
    assert implication(result is Relation.ENCLOSED,
                       relation_with_contour is Relation.TOUCH
                       or relation_with_contour is Relation.OVERLAP)
    assert implication(result is Relation.WITHIN,
                       relation_with_contour is Relation.DISJOINT)
    assert implication(relation_with_contour is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       or result is Relation.CROSS
                       or result is Relation.WITHIN)
    assert implication(relation_with_contour is Relation.TOUCH,
                       result is Relation.TOUCH
                       or result is Relation.CROSS
                       or result is Relation.ENCLOSED)
    assert implication(relation_with_contour is Relation.OVERLAP,
                       result is Relation.TOUCH
                       or result is Relation.CROSS
                       or result is Relation.ENCLOSED)


@given(strategies.contours_with_multisegments)
def test_reversals(region_with_multisegment: Tuple[Region, Multisegment]
                   ) -> None:
    region, multisegment = region_with_multisegment

    result = multisegment_in_region(multisegment, region)

    assert result is multisegment_in_region(
            reverse_multisegment(multisegment), region)
    assert result is multisegment_in_region(multisegment,
                                            reverse_contour(region))


@given(strategies.contours_with_multisegments)
def test_rotations(region_with_multisegment: Tuple[Region, Multisegment]
                   ) -> None:
    region, multisegment = region_with_multisegment

    result = multisegment_in_region(multisegment, region)

    assert all(result is multisegment_in_region(multisegment, rotated)
               for rotated in rotations(region))
    assert all(result is multisegment_in_region(rotated, region)
               for rotated in rotations(multisegment))
