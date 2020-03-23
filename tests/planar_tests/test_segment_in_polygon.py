from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.core.contour import edges
from orient.hints import (Polygon,
                          Segment)
from orient.planar import (PointLocation,
                           SegmentLocation,
                           point_in_polygon,
                           segment_in_polygon)
from tests.utils import (are_polygons_similar,
                         equivalence,
                         implication,
                         to_contour_separators,
                         to_convex_hull)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    assert isinstance(result, SegmentLocation)


@given(strategies.polygons_with_segments)
def test_outside(polygon_with_segment: Tuple[Polygon, Segment]) -> None:
    polygon, segment = polygon_with_segment

    result = segment_in_polygon(segment, polygon)

    start, end = segment
    assert implication(result is SegmentLocation.EXTERNAL,
                       point_in_polygon(start, polygon)
                       is PointLocation.EXTERNAL
                       and point_in_polygon(end, polygon)
                       is PointLocation.EXTERNAL)


@given(strategies.polygons)
def test_border_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is SegmentLocation.BOUNDARY
               for edge in edges(border))


@given(strategies.polygons)
def test_holes_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is SegmentLocation.BOUNDARY
               for edge in chain.from_iterable(map(edges, holes)))


@given(strategies.polygons)
def test_border_separators(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(segment, polygon)
               in (SegmentLocation.TOUCH, SegmentLocation.CROSS,
                   SegmentLocation.ENCLOSED)
               for segment in to_contour_separators(border))


@given(strategies.polygons)
def test_holes_separators(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(segment, polygon)
               in (SegmentLocation.TOUCH, SegmentLocation.CROSS,
                   SegmentLocation.ENCLOSED)
               for hole in holes
               for segment in to_contour_separators(hole))


@given(strategies.polygons)
def test_convex_polygon_criterion(polygon: Polygon) -> None:
    border, holes = polygon
    assert (bool(holes)
            or equivalence(all(segment_in_polygon(segment, polygon)
                               is SegmentLocation.ENCLOSED
                               for segment in to_contour_separators(border)),
                           are_polygons_similar(polygon,
                                                (to_convex_hull(border),
                                                 holes))))
