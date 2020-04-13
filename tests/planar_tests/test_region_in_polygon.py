from typing import Tuple

from hypothesis import given

from orient.hints import (Polygon,
                          Region)
from orient.planar import (Relation,
                           region_in_polygon)
from tests.utils import COMPOUND_RELATIONS
from . import strategies


@given(strategies.polygons_with_contours)
def test_basic(region_with_polygon: Tuple[Polygon, Region]) -> None:
    polygon, region = region_with_polygon

    result = region_in_polygon(region, polygon)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert region_in_polygon(region, (region, [])) is Relation.EQUAL
