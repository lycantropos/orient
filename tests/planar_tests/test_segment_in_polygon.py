from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.core.region import to_segments
from orient.hints import (Polygon,
                          Segment)
from orient.planar import (Relation,
                           point_in_polygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         are_polygons_similar,
                         implication,
                         to_contour_separators,
                         to_convex_hull)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.polygons_with_segments)
def test_outside(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_polygon(start, polygon) is Relation.DISJOINT
                       and point_in_polygon(end, polygon) is Relation.DISJOINT)


@given(strategies.polygons)
def test_border_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is Relation.COMPONENT
               for edge in to_segments(border))


@given(strategies.polygons)
def test_holes_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is Relation.COMPONENT
               for edge in chain.from_iterable(map(to_segments, holes)))


@given(strategies.polygons)
def test_border_separators(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(segment, polygon)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for segment in to_contour_separators(border))


@given(strategies.polygons)
def test_holes_separators(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(segment, polygon)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for hole in holes
               for segment in to_contour_separators(hole))


@given(strategies.polygons)
def test_convex_polygon(polygon: Polygon) -> None:
    border, holes = polygon
    polygon_with_convex_border = (to_convex_hull(border), holes)
    assert (bool(holes)
            or implication(are_polygons_similar(polygon,
                                                polygon_with_convex_border),
                           all(segment_in_polygon(segment, polygon)
                               is Relation.ENCLOSED
                               for segment in to_contour_separators(border))))
