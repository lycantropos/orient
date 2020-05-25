from typing import Tuple

from hypothesis import given

from orient.hints import Region
from orient.planar import (Relation,
                           contour_in_region,
                           point_in_region,
                           region_in_region)
from tests.utils import (ASYMMETRIC_COMPOUND_RELATIONS,
                         COMPOUND_RELATIONS,
                         SYMMETRIC_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         rotations,
                         to_convex_hull)
from . import strategies


@given(strategies.contours_pairs)
def test_basic(regions_pair: Tuple[Region, Region]) -> None:
    left_region, right_region = regions_pair

    result = region_in_region(left_region, right_region)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert region_in_region(region, region) is Relation.EQUAL


@given(strategies.contours_pairs)
def test_relations(regions_pair: Tuple[Region, Region]) -> None:
    left_region, right_region = regions_pair

    result = region_in_region(left_region, right_region)

    complement = region_in_region(right_region, left_region)
    assert equivalence(result is complement,
                       result in SYMMETRIC_COMPOUND_RELATIONS)
    assert equivalence(result is not complement
                       and result.complement is complement,
                       result in ASYMMETRIC_COMPOUND_RELATIONS
                       and complement in ASYMMETRIC_COMPOUND_RELATIONS)


@given(strategies.contours)
def test_convex_hull(region: Region) -> None:
    assert (region_in_region(region, to_convex_hull(region))
            in (Relation.EQUAL, Relation.ENCLOSED))


@given(strategies.contours_pairs)
def test_vertices(regions_pair: Tuple[Region, Region]) -> None:
    left_region, right_region = regions_pair

    assert implication(region_in_region(left_region, right_region)
                       in (Relation.EQUAL, Relation.COMPONENT,
                           Relation.ENCLOSED, Relation.WITHIN),
                       all(point_in_region(vertex, right_region)
                           is not Relation.DISJOINT
                           for vertex in left_region))


@given(strategies.contours_pairs)
def test_reversed(regions_pair: Tuple[Region, Region]) -> None:
    left, right = regions_pair

    result = region_in_region(left, right)

    assert result is region_in_region(reverse_contour(left), right)
    assert result is region_in_region(left, reverse_contour(right))


@given(strategies.contours_pairs)
def test_rotations(regions_pair: Tuple[Region, Region]) -> None:
    left, right = regions_pair

    result = region_in_region(left, right)

    assert all(result is region_in_region(rotated, right)
               for rotated in rotations(left))
    assert all(result is region_in_region(left, rotated)
               for rotated in rotations(right))


@given(strategies.contours_pairs)
def test_connection_with_contour_in_region(regions_pair: Tuple[Region, Region]
                                           ) -> None:
    left_region, right_region = regions_pair

    result = region_in_region(left_region, right_region)

    contour_relation = contour_in_region(left_region, right_region)
    assert equivalence(result is Relation.DISJOINT
                       or result is Relation.COVER,
                       contour_relation is Relation.DISJOINT)
    assert equivalence(result is Relation.TOUCH
                       or result is Relation.ENCLOSES
                       or result is Relation.COMPOSITE,
                       contour_relation is Relation.TOUCH)
    assert equivalence(result is Relation.OVERLAP,
                       contour_relation is Relation.CROSS)
    assert equivalence(result is Relation.COMPONENT
                       or result is Relation.EQUAL,
                       contour_relation is Relation.COMPONENT)
    assert equivalence(result is Relation.ENCLOSED,
                       contour_relation is Relation.ENCLOSED)
    assert equivalence(result is Relation.WITHIN,
                       contour_relation is Relation.WITHIN)
