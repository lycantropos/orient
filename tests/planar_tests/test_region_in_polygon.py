from typing import Tuple

from hypothesis import given

from orient.hints import (Polygon,
                          Region)
from orient.planar import (Relation,
                           region_in_polygon)
from . import strategies


@given(strategies.contours_with_polygons)
def test_basic(region_with_polygon: Tuple[Region, Polygon]) -> None:
    region, polygon = region_with_polygon

    result = region_in_polygon(region, polygon)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert region_in_polygon(region, (region, [])) is Relation.EQUAL
