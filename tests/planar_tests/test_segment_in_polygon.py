from typing import Tuple

from ground.base import Relation
from ground.hints import (Polygon,
                          Segment)
from hypothesis import given

from orient.planar import (point_in_polygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         are_polygons_equivalent,
                         implication,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         reverse_segment,
                         reverse_segment_coordinates,
                         to_contour_separators,
                         to_polygon_edges,
                         to_polygon_with_convex_border)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert all(segment_in_polygon(edge, polygon) is Relation.COMPONENT
               for edge in to_polygon_edges(polygon))


@given(strategies.polygons)
def test_separators(polygon: Polygon) -> None:
    assert all(segment_in_polygon(segment, polygon)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for segment in to_contour_separators(polygon.border))
    assert all(segment_in_polygon(segment, polygon)
               in (Relation.TOUCH, Relation.CROSS, Relation.ENCLOSED)
               for hole in polygon.holes
               for segment in to_contour_separators(hole))


@given(strategies.polygons)
def test_convex_polygon(polygon: Polygon) -> None:
    polygon_with_convex_border = to_polygon_with_convex_border(polygon)
    assert (bool(polygon.holes)
            or implication(
                    are_polygons_equivalent(polygon,
                                            polygon_with_convex_border),
                    all(segment_in_polygon(segment, polygon)
                        is Relation.ENCLOSED
                        for segment in to_contour_separators(polygon.border))))


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
    assert result is segment_in_polygon(reverse_segment_coordinates(segment),
                                        reverse_polygon_coordinates(polygon))


@given(strategies.polygons_with_segments)
def test_connection_with_point_in_polygon(polygon_with_segment
                                          : Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    assert implication(result is Relation.DISJOINT,
                       point_in_polygon(segment.start, polygon)
                       is point_in_polygon(segment.end, polygon)
                       is Relation.DISJOINT)
