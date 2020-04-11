from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Region)
from orient.planar import (Relation,
                           contour_in_region)
from . import strategies


@given(strategies.contours_pairs)
def test_basic(contour_with_region: Tuple[Contour, Region]) -> None:
    contour, region = contour_with_region

    result = contour_in_region(contour, region)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_region(contour, contour) is Relation.COMPONENT
