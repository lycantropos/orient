from fractions import Fraction
from functools import partial
from typing import (Optional,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from orient.hints import (Contour,
                          Coordinate,
                          Multicontour,
                          Multipolygon,
                          Multisegment,
                          Point,
                          Polygon,
                          Segment)
from tests.strategies import (coordinates_strategies,
                              rational_coordinates_strategies)
from tests.utils import (Strategy,
                         sub_lists,
                         to_pairs,
                         to_triplets)

points = coordinates_strategies.flatmap(planar.points)
segments = coordinates_strategies.flatmap(planar.segments)


def to_segments_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(planar.segments(coordinates),
                             planar.points(coordinates))


segments_with_points = coordinates_strategies.flatmap(to_segments_with_points)
segments_strategies = coordinates_strategies.map(planar.segments)
segments_pairs = segments_strategies.flatmap(to_pairs)
empty_multisegments = strategies.builds(list)
multisegments = coordinates_strategies.flatmap(planar.multisegments)
non_empty_multisegments = (coordinates_strategies
                           .flatmap(partial(planar.multisegments,
                                            min_size=1)))


def to_multisegments_with_points(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[Tuple[Multisegment, Point]]:
    return strategies.tuples(planar.multisegments(coordinates),
                             planar.points(coordinates))


multisegments_with_points = (coordinates_strategies
                             .flatmap(to_multisegments_with_points))
empty_multisegments_with_segments = strategies.tuples(empty_multisegments,
                                                      segments)


def to_multisegments_with_segments(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Multisegment, Segment]]:
    return strategies.tuples(planar.multisegments(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.segments(coordinates))


multisegments_with_segments = (coordinates_strategies
                               .flatmap(to_multisegments_with_segments))
non_empty_multisegments_with_segments = (
    coordinates_strategies.flatmap(partial(to_multisegments_with_segments,
                                           min_size=1)))


def chop_segment(segment: Segment, parts_count: int) -> Multisegment:
    if parts_count == 1:
        return [segment]
    (start_x, start_y), (end_x, end_y) = segment
    delta_x, delta_y = end_x - start_x, end_y - start_y
    step_x, step_y = (Fraction(delta_x, parts_count),
                      Fraction(delta_y, parts_count))
    end_x, end_y = start_x + step_x, start_y + step_y
    result = []
    for part_index in range(parts_count):
        result.append(((start_x, start_y), (end_x, end_y)))
        start_x, start_y = end_x, end_y
        end_x, end_y = start_x + step_x, start_y + step_y
    return result


def segment_to_multisegments_with_segments(segment: Segment,
                                           *,
                                           max_partition_size: int = 100
                                           ) -> Strategy[Tuple[Multisegment,
                                                               Segment]]:
    always_segment = strategies.just(segment)
    partition_sizes = strategies.integers(1, max_partition_size)
    return strategies.tuples((strategies.builds(chop_segment,
                                                always_segment,
                                                partition_sizes)
                              .flatmap(strategies.permutations)),
                             always_segment)


rational_segments = rational_coordinates_strategies.flatmap(planar.segments)
multisegments_with_segments |= (
    rational_segments.flatmap(segment_to_multisegments_with_segments))
multisegments_strategies = coordinates_strategies.map(planar.multisegments)


def to_multisegments_pairs(coordinates: Strategy[Coordinate],
                           *,
                           min_size: int = 0,
                           max_size: Optional[int] = None
                           ) -> Strategy[Tuple[Multisegment, Multisegment]]:
    return strategies.tuples(planar.multisegments(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.multisegments(coordinates))


multisegments_pairs = coordinates_strategies.flatmap(to_multisegments_pairs)
empty_multisegments_with_multisegments = strategies.tuples(empty_multisegments,
                                                           multisegments)
non_empty_multisegments_with_multisegments = (
    coordinates_strategies.flatmap(partial(to_multisegments_pairs,
                                           min_size=1)))
contours = coordinates_strategies.flatmap(planar.contours)


def to_contours_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Contour, Point]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.points(coordinates))


contours_with_points = coordinates_strategies.flatmap(to_contours_with_points)


def to_contours_with_segments(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Contour, Segment]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.segments(coordinates))


contours_with_segments = (coordinates_strategies
                          .flatmap(to_contours_with_segments))
contours_with_empty_multisegments = strategies.tuples(contours,
                                                      empty_multisegments)


def to_contours_with_multisegments(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Contour, Multisegment]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.multisegments(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


contours_with_multisegments = (coordinates_strategies
                               .flatmap(to_contours_with_multisegments))
contours_with_non_empty_multisegments = (
    coordinates_strategies.flatmap(partial(to_contours_with_multisegments,
                                           min_size=1)))
contours_strategies = coordinates_strategies.map(planar.contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)
empty_multicontours = strategies.builds(list)
multicontours = coordinates_strategies.flatmap(planar.multicontours)
non_empty_multicontours = (coordinates_strategies
                           .flatmap(partial(planar.multicontours,
                                            min_size=1)))


def to_multicontours_with_points(coordinates: Strategy[Coordinate],
                                 *,
                                 min_size: int = 0,
                                 max_size: Optional[int] = None
                                 ) -> Strategy[Tuple[Multicontour, Point]]:
    return strategies.tuples(planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.points(coordinates))


multicontours_with_points = (coordinates_strategies
                             .flatmap(to_multicontours_with_points))
empty_multicontours_with_points = strategies.tuples(empty_multicontours,
                                                    points)
non_empty_multicontours_with_points = coordinates_strategies.flatmap(
        partial(to_multicontours_with_points,
                min_size=1))
empty_multicontours_with_segments = strategies.tuples(empty_multicontours,
                                                      segments)


def to_multicontours_with_segments(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Multicontour, Segment]]:
    return strategies.tuples(planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.segments(coordinates))


multicontours_with_segments = (coordinates_strategies
                               .flatmap(to_multicontours_with_segments))
non_empty_multicontours_with_segments = coordinates_strategies.flatmap(
        partial(to_multicontours_with_segments,
                min_size=1))
multicontours_with_empty_multisegments = strategies.tuples(multicontours,
                                                           empty_multisegments)


def to_multicontours_with_multisegments(coordinates: Strategy[Coordinate],
                                        *,
                                        min_size: int = 0,
                                        max_size: Optional[int] = None
                                        ) -> Strategy[Tuple[Multicontour,
                                                            Multisegment]]:
    return strategies.tuples(planar.multicontours(coordinates),
                             planar.multisegments(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


multicontours_with_multisegments = (
    coordinates_strategies.flatmap(to_multicontours_with_multisegments))
multicontours_with_non_empty_multisegments = (
    coordinates_strategies.flatmap(partial(to_multicontours_with_multisegments,
                                           min_size=1)))


def to_multicontours_with_contours(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Multicontour, Contour]]:
    return strategies.tuples(planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.contours(coordinates))


multicontours_with_contours = (coordinates_strategies
                               .flatmap(to_multicontours_with_contours))
empty_multicontours_with_contours = strategies.tuples(empty_multicontours,
                                                      contours)
non_empty_multicontours_with_contours = coordinates_strategies.flatmap(
        partial(to_multicontours_with_contours,
                min_size=1))
empty_multicontours_with_multicontours = strategies.tuples(empty_multicontours,
                                                           multicontours)


def to_multicontours_pairs(coordinates: Strategy[Coordinate],
                           *,
                           min_size: int = 0,
                           max_size: Optional[int] = None
                           ) -> Strategy[Tuple[Multicontour, Multicontour]]:
    return strategies.tuples(planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.multicontours(coordinates))


multicontours_pairs = coordinates_strategies.flatmap(to_multicontours_pairs)
non_empty_multicontours_with_multicontours = (
    coordinates_strategies.flatmap(partial(to_multicontours_pairs,
                                           min_size=1)))
polygons = coordinates_strategies.flatmap(planar.polygons)


def to_polygons_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Polygon, Point]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.points(coordinates))


polygons_with_points = coordinates_strategies.flatmap(to_polygons_with_points)


def to_polygons_with_segments(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Polygon, Segment]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.segments(coordinates))


polygons_with_segments = (coordinates_strategies
                          .flatmap(to_polygons_with_segments))


def to_polygons_with_multisegments(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Polygon, Multisegment]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.multisegments(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


polygons_with_multisegments = (
    coordinates_strategies.flatmap(to_polygons_with_multisegments))
polygons_with_empty_multisegments = strategies.tuples(polygons,
                                                      empty_multisegments)
polygons_with_non_empty_multisegments = (
    coordinates_strategies.flatmap(partial(to_polygons_with_multisegments,
                                           min_size=1)))


def to_polygons_with_contours(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Polygon, Contour]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.contours(coordinates))


polygons_with_contours = (coordinates_strategies
                          .flatmap(to_polygons_with_contours))
polygons_with_empty_multicontours = strategies.tuples(polygons,
                                                      empty_multicontours)


def to_polygons_with_multicontours(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Polygon, Multicontour]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


def polygon_to_polygon_with_multicontours(polygon: Polygon
                                          ) -> Strategy[Tuple[Polygon,
                                                              Multicontour]]:
    _, holes = polygon
    return strategies.tuples(strategies.just(polygon), sub_lists(holes))


polygons_with_multicontours = (
        polygons.flatmap(polygon_to_polygon_with_multicontours)
        | coordinates_strategies.flatmap(to_polygons_with_multicontours))
polygons_with_non_empty_multicontours = (
    coordinates_strategies.flatmap(partial(to_polygons_with_multicontours,
                                           min_size=1)))
polygons_strategies = coordinates_strategies.map(planar.polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
empty_multipolygons = strategies.builds(list)
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)
non_empty_multipolygons = (coordinates_strategies
                           .flatmap(partial(planar.multipolygons,
                                            min_size=1)))
empty_multipolygons_with_points = strategies.tuples(empty_multipolygons,
                                                    points)


def to_multipolygons_with_points(coordinates: Strategy[Coordinate],
                                 *,
                                 min_size: int = 0,
                                 max_size: Optional[int] = None
                                 ) -> Strategy[Tuple[Multipolygon, Point]]:
    return strategies.tuples(planar.multipolygons(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.points(coordinates))


multipolygons_with_points = (coordinates_strategies
                             .flatmap(to_multipolygons_with_points))
non_empty_multipolygons_with_points = (
    coordinates_strategies.flatmap(partial(to_multipolygons_with_points,
                                           min_size=1)))
empty_multipolygons_with_segments = strategies.tuples(empty_multipolygons,
                                                      segments)


def to_multipolygons_with_segments(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Multipolygon, Segment]]:
    return strategies.tuples(planar.multipolygons(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.segments(coordinates))


multipolygons_with_segments = (coordinates_strategies
                               .flatmap(to_multipolygons_with_segments))
non_empty_multipolygons_with_segments = coordinates_strategies.flatmap(
        partial(to_multipolygons_with_segments,
                min_size=1))
multipolygons_with_empty_multisegments = strategies.tuples(multipolygons,
                                                           empty_multisegments)


def to_multipolygons_with_multisegments(coordinates: Strategy[Coordinate],
                                        *,
                                        min_size: int = 0,
                                        max_size: Optional[int] = None
                                        ) -> Strategy[Tuple[Multipolygon,
                                                            Multisegment]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multisegments(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


multipolygons_with_multisegments = (
    coordinates_strategies.flatmap(to_multipolygons_with_multisegments))
multipolygons_with_non_empty_multisegments = (
    coordinates_strategies.flatmap(partial(to_multipolygons_with_multisegments,
                                           min_size=1)))
empty_multipolygons_with_contours = strategies.tuples(empty_multipolygons,
                                                      contours)


def to_multipolygons_with_contours(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Multipolygon, Contour]]:
    return strategies.tuples(planar.multipolygons(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.contours(coordinates))


multipolygons_with_contours = (coordinates_strategies
                               .flatmap(to_multipolygons_with_contours))
non_empty_multipolygons_with_contours = coordinates_strategies.flatmap(
        partial(to_multipolygons_with_contours,
                min_size=1))
multipolygons_with_empty_multicontours = strategies.tuples(multipolygons,
                                                           empty_multicontours)


def to_multipolygons_with_multicontours(coordinates: Strategy[Coordinate],
                                        *,
                                        min_size: int = 0,
                                        max_size: Optional[int] = None
                                        ) -> Strategy[Tuple[Multipolygon,
                                                            Multicontour]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


multipolygons_with_multicontours = (
    coordinates_strategies.flatmap(to_multipolygons_with_multicontours))
multipolygons_with_non_empty_multicontours = (
    coordinates_strategies.flatmap(partial(to_multipolygons_with_multicontours,
                                           min_size=1)))
empty_multipolygons_with_polygons = strategies.tuples(empty_multipolygons,
                                                      polygons)


def to_multipolygons_with_polygons(coordinates: Strategy[Coordinate],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[Tuple[Multipolygon, Polygon]]:
    return strategies.tuples(planar.multipolygons(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.polygons(coordinates))


multipolygons_with_polygons = (coordinates_strategies
                               .flatmap(to_multipolygons_with_polygons))
non_empty_multipolygons_with_polygons = coordinates_strategies.flatmap(
        partial(to_multipolygons_with_polygons,
                min_size=1))
empty_multipolygons_with_multipolygons = strategies.tuples(empty_multipolygons,
                                                           multipolygons)


def to_multipolygons_pairs(coordinates: Strategy[Coordinate],
                           *,
                           min_size: int = 0,
                           max_size: Optional[int] = None
                           ) -> Strategy[Tuple[Multipolygon, Multipolygon]]:
    return strategies.tuples(planar.multipolygons(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.multipolygons(coordinates))


multipolygons_pairs = coordinates_strategies.flatmap(to_multipolygons_pairs)
non_empty_multipolygons_with_multipolygons = (
    coordinates_strategies.flatmap(partial(to_multipolygons_pairs,
                                           min_size=1)))
