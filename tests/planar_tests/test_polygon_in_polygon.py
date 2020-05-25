from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import Polygon
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
                         to_convex_hull)
from . import strategies


@given(strategies.polygons_pairs)
def test_basic(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    result = polygon_in_polygon(left_polygon, right_polygon)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert polygon_in_polygon(polygon, polygon) is Relation.EQUAL


@given(strategies.polygons_pairs)
def test_relations(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    result = polygon_in_polygon(left_polygon, right_polygon)

    complement = polygon_in_polygon(right_polygon, left_polygon)
    assert equivalence(result is complement,
                       result in SYMMETRIC_COMPOUND_RELATIONS)
    assert equivalence(result is not complement
                       and result.complement is complement,
                       result in ASYMMETRIC_COMPOUND_RELATIONS
                       and complement in ASYMMETRIC_COMPOUND_RELATIONS)


@given(strategies.polygons)
def test_border_convex_hull(polygon: Polygon) -> None:
    border, holes = polygon
    assert (polygon_in_polygon(polygon, (to_convex_hull(border), holes))
            in (Relation.EQUAL, Relation.ENCLOSED))


@given(strategies.polygons)
def test_without_holes(polygon: Polygon) -> None:
    border, holes = polygon
    polygon_without_holes = (border, [])
    assert (polygon_in_polygon(polygon, polygon_without_holes)
            is (Relation.ENCLOSED if holes else Relation.EQUAL))
    assert (polygon_in_polygon(polygon_without_holes, polygon)
            is (Relation.ENCLOSES if holes else Relation.EQUAL))


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
    left_polygon, right_polygon = polygons_pair

    left_border, left_holes = left_polygon
    assert implication(polygon_in_polygon(left_polygon, right_polygon)
                       in (Relation.EQUAL, Relation.COMPONENT,
                           Relation.ENCLOSED, Relation.WITHIN),
                       all(point_in_polygon(vertex, right_polygon)
                           is not Relation.DISJOINT
                           for vertex in chain(left_border, *left_holes)))
