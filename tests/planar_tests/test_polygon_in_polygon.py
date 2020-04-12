from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import Polygon
from orient.planar import (Relation,
                           point_in_polygon,
                           polygon_in_polygon)
from tests.utils import (COMPOUND_RELATIONS,
                         equivalence,
                         implication,
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
def test_symmetric_relations(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    result = polygon_in_polygon(left_polygon, right_polygon)

    complement = polygon_in_polygon(right_polygon, left_polygon)
    assert equivalence(result is complement,
                       result in (Relation.DISJOINT, Relation.TOUCH,
                                  Relation.OVERLAP, Relation.EQUAL))


@given(strategies.polygons_pairs)
def test_asymmetric_relations(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    result = polygon_in_polygon(left_polygon, right_polygon)

    complement = polygon_in_polygon(right_polygon, left_polygon)
    assert equivalence(result is Relation.COVER, complement is Relation.WITHIN)
    assert equivalence(result is Relation.ENCLOSES,
                       complement is Relation.ENCLOSED)
    assert equivalence(result is Relation.COMPOSITE,
                       complement is Relation.COMPONENT)


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
def test_vertices(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    left_border, left_holes = left_polygon
    assert implication(polygon_in_polygon(left_polygon, right_polygon)
                       in (Relation.EQUAL, Relation.COMPONENT,
                           Relation.ENCLOSED, Relation.WITHIN),
                       all(point_in_polygon(vertex, right_polygon)
                           is not Relation.DISJOINT
                           for vertex in chain(left_border, *left_holes)))
