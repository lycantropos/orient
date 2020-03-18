from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Point)
from orient.planar import (PointLocation,
                           point_in_contour)
from . import strategies


@given(strategies.contours_with_points)
def test_basic(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert isinstance(result, PointLocation)


@given(strategies.contours)
def test_contour(contour: Contour) -> None:
    assert all(point_in_contour(vertex, contour) is PointLocation.BOUNDARY
               for vertex in contour)
