from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Point)
from orient.planar import (PointPolygonLocation,
                           point_in_polygon)
from . import strategies


@given(strategies.contours_with_points)
def test_basic(border_with_point: Tuple[Contour, Point]) -> None:
    border, point = border_with_point

    result = point_in_polygon(point, border)

    assert isinstance(result, PointPolygonLocation)


@given(strategies.contours)
def test_contour(border: Contour) -> None:
    assert all(point_in_polygon(vertex,
                                border) is PointPolygonLocation.BOUNDARY
               for vertex in border)
