from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import (Point,
                          Polygon)
from orient.planar import (PointLocation,
                           point_in_polygon)
from tests.utils import implication
from . import strategies


@given(strategies.polygons_with_points)
def test_basic(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    assert isinstance(result, PointLocation)


@given(strategies.polygons)
def test_vertices(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(point_in_polygon(vertex, polygon) is PointLocation.BOUNDARY
               for vertex in chain(border, *holes))


@given(strategies.polygons_with_points)
def test_solid(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    border, holes = polygon
    assert implication(result is PointLocation.INSIDE,
                       point_in_polygon(point, (border, []))
                       is PointLocation.INSIDE)
    assert implication(point_in_polygon(point, (border, []))
                       is PointLocation.OUTSIDE,
                       result is PointLocation.OUTSIDE)
    assert implication(point_in_polygon(point, (border, []))
                       is PointLocation.BOUNDARY,
                       result is PointLocation.BOUNDARY)
