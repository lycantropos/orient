from typing import Tuple

from ground.hints import Polygon
from hypothesis import given

from orient.planar import (Relation,
                           point_in_polygon,
                           polygon_in_polygon)
from tests.utils import (ASYMMETRIC_COMPOUND_RELATIONS,
                         COMPOUND_RELATIONS,
                         SYMMETRIC_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         to_polygon_vertices, to_polygon_with_convex_border,
                         to_solid_polygon)
from . import strategies


@given(strategies.polygons_pairs)
def test_basic(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left, right = polygons_pair

    result = polygon_in_polygon(left, right)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert polygon_in_polygon(polygon, polygon) is Relation.EQUAL


@given(strategies.polygons_pairs)
def test_relations(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left, right = polygons_pair

    result = polygon_in_polygon(left, right)

    complement = polygon_in_polygon(right, left)
    assert equivalence(result is complement,
                       result in SYMMETRIC_COMPOUND_RELATIONS)
    assert equivalence(result is not complement,
                       result.complement is complement
                       and result in ASYMMETRIC_COMPOUND_RELATIONS
                       and complement in ASYMMETRIC_COMPOUND_RELATIONS)


@given(strategies.polygons)
def test_border_convex_hull(polygon: Polygon) -> None:
    assert (polygon_in_polygon(polygon, to_polygon_with_convex_border(polygon))
            in (Relation.EQUAL, Relation.ENCLOSED))


@given(strategies.polygons)
def test_without_holes(polygon: Polygon) -> None:
    solid_polygon = to_solid_polygon(polygon)
    assert (polygon_in_polygon(polygon, solid_polygon)
            is (Relation.ENCLOSED if polygon.holes else Relation.EQUAL))
    assert (polygon_in_polygon(solid_polygon, polygon)
            is (Relation.ENCLOSES if polygon.holes else Relation.EQUAL))


@given(strategies.polygons_pairs)
def test_reversals(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left, right = polygons_pair

    result = polygon_in_polygon(left, right)

    assert result is polygon_in_polygon(reverse_polygon_border(left), right)
    assert result is polygon_in_polygon(left, reverse_polygon_border(right))
    assert result is polygon_in_polygon(reverse_polygon_holes(left), right)
    assert result is polygon_in_polygon(left, reverse_polygon_holes(right))
    assert result is polygon_in_polygon(reverse_polygon_holes_contours(left),
                                        right)
    assert result is polygon_in_polygon(left,
                                        reverse_polygon_holes_contours(right))


@given(strategies.polygons_pairs)
def test_connection_with_point_in_polygon(polygons_pair
                                          : Tuple[Polygon, Polygon]) -> None:
    left, right = polygons_pair

    assert implication(polygon_in_polygon(left, right)
                       in (Relation.EQUAL, Relation.COMPONENT,
                           Relation.ENCLOSED, Relation.WITHIN),
                       all(point_in_polygon(vertex, right)
                           is not Relation.DISJOINT
                           for vertex in to_polygon_vertices(left)))
