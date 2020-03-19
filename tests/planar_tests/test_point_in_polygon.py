from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import (Point,
                          Polygon)
from orient.planar import (PointLocation,
                           point_in_polygon)
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
