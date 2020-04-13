from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Polygon)
from orient.planar import (Relation,
                           contour_in_polygon)
from tests.utils import LINEAR_COMPOUND_RELATIONS
from . import strategies


@given(strategies.polygons_with_contours)
def test_basic(polygon_with_contour: Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_polygon(contour, (contour, [])) is Relation.COMPONENT
