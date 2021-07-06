from typing import Tuple

from ground.base import Location
from ground.hints import (Contour,
                          Point)
from hypothesis import given

from orient.planar import point_in_contour
from tests.utils import (LINEAR_LOCATIONS,
                         contour_rotations,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_point_coordinates)
from . import strategies


@given(strategies.contours_with_points)
def test_basic(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert isinstance(result, Location)
    assert result in LINEAR_LOCATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert all(point_in_contour(vertex, contour) is Location.BOUNDARY
               for vertex in contour.vertices)


@given(strategies.contours_with_points)
def test_reversals(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert result is point_in_contour(point, reverse_contour(contour))
    assert result is point_in_contour(reverse_point_coordinates(point),
                                      reverse_contour_coordinates(contour))


@given(strategies.contours_with_points)
def test_rotations(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert all(result is point_in_contour(point, rotated)
               for rotated in contour_rotations(contour))
