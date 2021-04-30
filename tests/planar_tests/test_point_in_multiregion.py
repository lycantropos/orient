from typing import Tuple

from ground.base import Relation
from ground.hints import Point
from hypothesis import given

from orient.hints import Multiregion
from orient.planar import (point_in_multiregion,
                           point_in_region)
from tests.utils import (PRIMITIVE_COMPOUND_RELATIONS,
                         equivalence,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_multiregion_regions,
                         reverse_point_coordinates,
                         sequence_rotations)
from . import strategies


@given(strategies.multiregions_with_points)
def test_basic(multiregion_with_point: Tuple[Multiregion, Point]) -> None:
    multiregion, point = multiregion_with_point

    result = point_in_multiregion(point, multiregion)

    assert isinstance(result, Relation)
    assert result in PRIMITIVE_COMPOUND_RELATIONS


@given(strategies.multiregions)
def test_vertices(multiregion: Multiregion) -> None:
    assert all(point_in_multiregion(vertex, multiregion) is Relation.COMPONENT
               for region in multiregion
               for vertex in region.vertices)


@given(strategies.multiregions_with_points)
def test_step(multiregion_with_region: Tuple[Multiregion, Point]) -> None:
    multiregion, point = multiregion_with_region
    first_region, *rest_multiregion = multiregion

    result = point_in_multiregion(point, rest_multiregion)
    next_result = point_in_multiregion(point, multiregion)

    relation_with_first_region = point_in_region(point, first_region)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       and relation_with_first_region is Relation.DISJOINT)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_region is Relation.WITHIN)
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_region is Relation.COMPONENT)


@given(strategies.multiregions_with_points)
def test_reversals(multiregion_with_point: Tuple[Multiregion, Point]) -> None:
    multiregion, point = multiregion_with_point

    result = point_in_multiregion(point, multiregion)

    assert result is point_in_multiregion(point,
                                          reverse_multiregion(multiregion))
    assert result is point_in_multiregion(
            point, reverse_multiregion_regions(multiregion))
    assert result is point_in_multiregion(
            reverse_point_coordinates(point),
            reverse_multiregion_coordinates(multiregion))


@given(strategies.multiregions_with_points)
def test_rotations(multiregion_with_point: Tuple[Multiregion, Point]) -> None:
    multiregion, point = multiregion_with_point

    result = point_in_multiregion(point, multiregion)

    assert all(result is point_in_multiregion(point, rotated)
               for rotated in sequence_rotations(multiregion))
