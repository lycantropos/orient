from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.core.contour import to_segments
from orient.hints import (Polygon,
                          Segment)
from orient.planar import (PointLocation,
                           SegmentLocation,
                           point_in_polygon,
                           segment_in_polygon)
from tests.utils import (are_polygons_similar,
                         equivalence,
                         implication,
                         to_convex_hull,
                         to_non_edge_rays)
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
    assert implication(result is SegmentLocation.OUTSIDE,
                       point_in_polygon(start, polygon)
                       is PointLocation.OUTSIDE
                       and point_in_polygon(end, polygon)
                       is PointLocation.OUTSIDE)


@given(strategies.polygons)
def test_border_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is SegmentLocation.BOUNDARY
               for edge in to_segments(border))


@given(strategies.polygons)
def test_holes_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert all(segment_in_polygon(edge, polygon) is SegmentLocation.BOUNDARY
               for edge in chain.from_iterable(map(to_segments, holes)))


@given(strategies.polygons)
def test_convex_polygon_criterion(polygon: Polygon) -> None:
    border, holes = polygon
    assert (bool(holes)
            or equivalence(all(segment_in_polygon(ray, polygon)
                               is SegmentLocation.INSIDE
                               for ray in to_non_edge_rays(border)),
                           are_polygons_similar(polygon,
                                                (to_convex_hull(border),
                                                 holes))))
