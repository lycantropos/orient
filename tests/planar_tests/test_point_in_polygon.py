from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import (Point,
                          Polygon)
from orient.planar import (Relation,
                           point_in_polygon)
from tests.utils import (PRIMITIVE_COMPOUND_RELATIONS,
                         implication,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours)
from . import strategies


@given(strategies.polygons_with_points)
def test_basic(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    assert isinstance(result, Relation)
    assert result in PRIMITIVE_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_vertices(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(point_in_polygon(vertex, polygon) is Relation.COMPONENT
               for vertex in chain(border, *holes))


@given(strategies.polygons_with_points)
def test_without_holes(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    border, holes = polygon
    polygon_without_holes = (border, [])
    assert implication(result is Relation.WITHIN,
                       point_in_polygon(point, polygon_without_holes)
                       is Relation.WITHIN)
    assert implication(point_in_polygon(point, polygon_without_holes)
                       is Relation.DISJOINT,
                       result is Relation.DISJOINT)
    assert implication(point_in_polygon(point, polygon_without_holes)
                       is Relation.COMPONENT,
                       result is Relation.COMPONENT)


@given(strategies.polygons_with_points)
def test_reversed(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    assert result is point_in_polygon(point, reverse_polygon_border(polygon))
    assert result is point_in_polygon(point, reverse_polygon_holes(polygon))
    assert result is point_in_polygon(point,
                                      reverse_polygon_holes_contours(polygon))
