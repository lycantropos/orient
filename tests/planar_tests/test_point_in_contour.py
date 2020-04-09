from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Point)
from orient.planar import (Relation,
                           point_in_contour)
from tests.utils import rotate_sequence
from . import strategies


@given(strategies.contours_with_points)
def test_basic(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_vertices(contour: Contour) -> None:
    assert all(point_in_contour(vertex, contour) is Relation.COMPONENT
               for vertex in contour)


@given(strategies.contours_with_points)
def test_reversed(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert result is point_in_contour(point, contour[::-1])


@given(strategies.contours_with_points)
def test_rotated(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    result = point_in_contour(point, contour)

    assert all(result is point_in_contour(point,
                                          rotate_sequence(contour, offset))
               for offset in range(1, len(contour)))
