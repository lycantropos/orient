from typing import Tuple

from hypothesis import given

from orient.hints import (Polygon,
                          Region)
from orient.planar import (Relation,
                           contour_in_polygon,
                           region_in_polygon)
from tests.utils import (COMPOUND_RELATIONS,
                         equivalence)
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


@given(strategies.polygons_with_contours)
def test_connection_with_contour_in_polygon(polygon_with_region
                                            : Tuple[Polygon, Region]
                                            ) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    contour_relation = contour_in_polygon(region, polygon)
    assert equivalence(result is Relation.DISJOINT
                       or result is Relation.COVER,
                       contour_relation is Relation.DISJOINT)
    assert equivalence(result is Relation.TOUCH
                       or result is Relation.ENCLOSES
                       or result is Relation.COMPOSITE,
                       contour_relation is Relation.TOUCH)
    assert equivalence(result is Relation.OVERLAP,
                       contour_relation is Relation.CROSS)
    assert equivalence(result is Relation.COMPONENT
                       or result is Relation.EQUAL,
                       contour_relation is Relation.COMPONENT)
    assert equivalence(result is Relation.ENCLOSED,
                       contour_relation is Relation.ENCLOSED)
    assert equivalence(result is Relation.WITHIN,
                       contour_relation is Relation.WITHIN)
