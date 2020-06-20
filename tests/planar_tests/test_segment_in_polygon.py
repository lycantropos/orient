from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.core.region import to_oriented_segments
from orient.hints import (Polygon,
                          Segment)
from orient.planar import (Relation,
                           point_in_polygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         are_polygons_similar,
                         implication,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         reverse_segment,
                         to_contour_separators,
                         to_convex_hull)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is Relation.COMPONENT
               for edge in to_oriented_segments(border))
    assert all(segment_in_polygon(edge, polygon) is Relation.COMPONENT
               for edge in chain.from_iterable(map(to_oriented_segments, holes)))


@given(strategies.polygons)
def test_separators(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(segment, polygon)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for segment in to_contour_separators(border))
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


@given(strategies.polygons_with_segments)
def test_reversals(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    assert result is segment_in_polygon(reverse_segment(segment), polygon)
    assert result is segment_in_polygon(segment,
                                        reverse_polygon_border(polygon))
    assert result is segment_in_polygon(segment,
                                        reverse_polygon_holes(polygon))
    assert result is segment_in_polygon(
            segment, reverse_polygon_holes_contours(polygon))


@given(strategies.polygons_with_segments)
def test_connection_with_point_in_polygon(polygon_with_segment
                                          : Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_polygon(start, polygon) is Relation.DISJOINT
                       and point_in_polygon(end, polygon) is Relation.DISJOINT)
