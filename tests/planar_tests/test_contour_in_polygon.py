from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Polygon)
from orient.planar import (Relation,
                           contour_in_polygon)
from . import strategies


@given(strategies.contours_with_polygons)
def test_basic(contour_with_polygon: Tuple[Contour, Polygon]) -> None:
    contour, polygon = contour_with_polygon

    result = contour_in_polygon(contour, polygon)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_polygon(contour, (contour, [])) is Relation.COMPONENT
