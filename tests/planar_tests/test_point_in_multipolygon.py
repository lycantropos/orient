from typing import Tuple

from ground.base import Relation
from ground.hints import (Multipolygon,
                          Point)
from hypothesis import given

from orient.planar import (point_in_multipolygon,
                           point_in_polygon)
from tests.utils import (PRIMITIVE_COMPOUND_RELATIONS,
                         equivalence,
                         multipolygon_pop_left,
                         multipolygon_rotations,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         to_multipolygon_vertices)
from . import strategies


@given(strategies.multipolygons_with_points)
def test_basic(multipolygon_with_point: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_point

    result = point_in_multipolygon(point, multipolygon)

    assert isinstance(result, Relation)
    assert result in PRIMITIVE_COMPOUND_RELATIONS


@given(strategies.multipolygons)
def test_vertices(multipolygon: Multipolygon) -> None:
    assert all(point_in_multipolygon(vertex, multipolygon)
               is Relation.COMPONENT
               for vertex in to_multipolygon_vertices(multipolygon))


@given(strategies.empty_multipolygons_with_points)
def test_base(multipolygon_with_polygon: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_polygon

    assert point_in_multipolygon(point, multipolygon) is Relation.DISJOINT


@given(strategies.non_empty_multipolygons_with_points)
def test_step(multipolygon_with_polygon: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_polygon
    first_polygon, rest_multipolygon = multipolygon_pop_left(multipolygon)

    result = point_in_multipolygon(point, rest_multipolygon)
    next_result = point_in_multipolygon(point, multipolygon)

    relation_with_first_polygon = point_in_polygon(point, first_polygon)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       and relation_with_first_polygon is Relation.DISJOINT)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_polygon is Relation.WITHIN)
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_polygon is Relation.COMPONENT)


@given(strategies.multipolygons_with_points)
def test_reversals(multipolygon_with_point: Tuple[Multipolygon, Point]
                   ) -> None:
    multipolygon, point = multipolygon_with_point

    result = point_in_multipolygon(point, multipolygon)

    assert result is point_in_multipolygon(point,
                                           reverse_multipolygon(multipolygon))
    assert result is point_in_multipolygon(
            point, reverse_multipolygon_borders(multipolygon))
    assert result is point_in_multipolygon(
            point, reverse_multipolygon_holes(multipolygon))
    assert result is point_in_multipolygon(
            point, reverse_multipolygon_holes_contours(multipolygon))


@given(strategies.multipolygons_with_points)
def test_rotations(multipolygon_with_point: Tuple[Multipolygon, Point]
                   ) -> None:
    multipolygon, point = multipolygon_with_point

    result = point_in_multipolygon(point, multipolygon)

    assert all(result is point_in_multipolygon(point, rotated)
               for rotated in multipolygon_rotations(multipolygon))
