from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import (Point,
                          Polygon)
from orient.planar import (Relation,
                           point_in_polygon)
from tests.utils import implication
from . import strategies


@given(strategies.polygons_with_points)
def test_basic(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    assert isinstance(result, Relation)


@given(strategies.polygons)
def test_vertices(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(point_in_polygon(vertex, polygon) is Relation.COMPONENT
               for vertex in chain(border, *holes))


@given(strategies.polygons_with_points)
def test_solid(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    border, holes = polygon
    assert implication(result is Relation.WITHIN,
                       point_in_polygon(point, (border, []))
                       is Relation.WITHIN)
    assert implication(point_in_polygon(point, (border, []))
                       is Relation.DISJOINT,
                       result is Relation.DISJOINT)
    assert implication(point_in_polygon(point, (border, []))
                       is Relation.COMPONENT,
                       result is Relation.COMPONENT)
