from typing import Tuple

from hypothesis import given

from orient.hints import Region
from orient.planar import (Relation,
                           point_in_region,
                           region_in_region)
from tests.utils import (equivalence,
                         implication,
                         to_convex_hull)
from . import strategies


@given(strategies.contours_pairs)
def test_basic(regions_pair: Tuple[Region, Region]) -> None:
    left_region, right_region = regions_pair

    result = region_in_region(left_region, right_region)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert region_in_region(region, region) is Relation.EQUAL


@given(strategies.contours_pairs)
def test_symmetric_relations(regions_pair: Tuple[Region, Region]) -> None:
    left_region, right_region = regions_pair

    result = region_in_region(left_region, right_region)

    complement = region_in_region(right_region, left_region)
    assert equivalence(result is complement,
                       result in (Relation.DISJOINT, Relation.TOUCH,
                                  Relation.OVERLAP, Relation.EQUAL))


@given(strategies.contours_pairs)
def test_asymmetric_relations(regions_pair: Tuple[Region, Region]) -> None:
    left_region, right_region = regions_pair

    result = region_in_region(left_region, right_region)

    complement = region_in_region(right_region, left_region)
    assert equivalence(result is Relation.COVER, complement is Relation.WITHIN)
    assert equivalence(result is Relation.ENCLOSES,
                       complement is Relation.ENCLOSED)
    assert equivalence(result is Relation.COMPOSITE,
                       complement is Relation.COMPONENT)


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
