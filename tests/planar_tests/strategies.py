from fractions import Fraction
from typing import (Optional,
                    Sequence,
                    Tuple)

from ground.hints import Scalar
from hypothesis import strategies
from hypothesis_geometry import planar

from orient.hints import Multiregion
from tests.strategies import (coordinates_strategies,
                              rational_coordinates_strategies)
from tests.utils import (Contour,
                         Multipolygon,
                         Multisegment,
                         Point,
                         Polygon,
                         Segment,
                         Strategy,
                         sub_lists,
                         to_multipolygon_edges,
                         to_pairs,
                         to_polygon_edges,
                         to_triplets)

points = coordinates_strategies.flatmap(planar.points)
segments = coordinates_strategies.flatmap(planar.segments)


def to_segments_with_points(coordinates: Strategy[Scalar]
                            ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(planar.segments(coordinates),
                             planar.points(coordinates))


segments_with_points = coordinates_strategies.flatmap(to_segments_with_points)
segments_strategies = coordinates_strategies.map(planar.segments)
segments_pairs = segments_strategies.flatmap(to_pairs)
multisegments = coordinates_strategies.flatmap(planar.multisegments)


def to_multisegments_with_points(coordinates: Strategy[Scalar]
                                 ) -> Strategy[Tuple[Multisegment, Point]]:
    return strategies.tuples(planar.multisegments(coordinates),
                             planar.points(coordinates))


multisegments_with_points = (coordinates_strategies
                             .flatmap(to_multisegments_with_points))


def to_multisegments_with_segments(coordinates: Strategy[Scalar]
                                   ) -> Strategy[Tuple[Multisegment, Segment]]:
    return strategies.tuples(planar.multisegments(coordinates),
                             planar.segments(coordinates))


multisegments_with_segments = (coordinates_strategies
                               .flatmap(to_multisegments_with_segments))


def chop_segment(segment: Segment, parts_count: int) -> Sequence[Segment]:
    if parts_count == 1:
        return [segment]
    delta_x, delta_y = (segment.end.x - segment.start.x,
                        segment.end.y - segment.start.y)
    step_x, step_y = (Fraction(delta_x, parts_count),
                      Fraction(delta_y, parts_count))
    start_x, start_y = segment.start.x, segment.start.y
    end_x, end_y = start_x + step_x, start_y + step_y
    result = []
    for part_index in range(parts_count):
        result.append(Segment(Point(start_x, start_y), Point(end_x, end_y)))
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
                              .flatmap(strategies.permutations))
                             .map(Multisegment),
                             always_segment)


rational_segments = rational_coordinates_strategies.flatmap(planar.segments)
multisegments_with_segments |= (
    rational_segments.flatmap(segment_to_multisegments_with_segments))
multisegments_strategies = coordinates_strategies.map(planar.multisegments)
multisegments_pairs = (coordinates_strategies.map(planar.multisegments)
                       .flatmap(to_pairs))
contours = coordinates_strategies.flatmap(planar.contours)


def to_contours_with_points(coordinates: Strategy[Scalar]
                            ) -> Strategy[Tuple[Contour, Point]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.points(coordinates))


contours_with_points = coordinates_strategies.flatmap(to_contours_with_points)


def to_contours_with_segments(coordinates: Strategy[Scalar]
                              ) -> Strategy[Tuple[Contour, Segment]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.segments(coordinates))


contours_with_segments = (coordinates_strategies
                          .flatmap(to_contours_with_segments))


def to_contours_with_multisegments(coordinates: Strategy[Scalar]
                                   ) -> Strategy[Tuple[Contour, Multisegment]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.multisegments(coordinates))


contours_with_multisegments = (coordinates_strategies
                               .flatmap(to_contours_with_multisegments))
contours_strategies = coordinates_strategies.map(planar.contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)
multiregions = coordinates_strategies.flatmap(planar.multicontours)


def to_multiregions_with_points(coordinates: Strategy[Scalar],
                                *,
                                min_size: int = 0,
                                max_size: Optional[int] = None
                                ) -> Strategy[Tuple[Multiregion, Point]]:
    return strategies.tuples(planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.points(coordinates))


multiregions_with_points = (coordinates_strategies
                            .flatmap(to_multiregions_with_points))


def to_multiregions_with_segments(coordinates: Strategy[Scalar],
                                  *,
                                  min_size: int = 0,
                                  max_size: Optional[int] = None
                                  ) -> Strategy[Tuple[Multiregion, Segment]]:
    return strategies.tuples(planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size),
                             planar.segments(coordinates))


multiregions_with_segments = (coordinates_strategies
                              .flatmap(to_multiregions_with_segments))


def to_multiregions_with_multisegments(coordinates: Strategy[Scalar]
                                       ) -> Strategy[Tuple[Multiregion,
                                                           Multisegment]]:
    return strategies.tuples(planar.multicontours(coordinates),
                             planar.multisegments(coordinates))


multiregions_with_multisegments = (
    coordinates_strategies.flatmap(to_multiregions_with_multisegments))


def to_multiregions_with_contours(coordinates: Strategy[Scalar]
                                  ) -> Strategy[Tuple[Multiregion, Contour]]:
    return strategies.tuples(planar.multicontours(coordinates),
                             planar.contours(coordinates))


multiregions_with_contours = (coordinates_strategies
                              .flatmap(to_multiregions_with_contours))


def to_multiregions_pairs(coordinates: Strategy[Scalar]
                          ) -> Strategy[Tuple[Multiregion, Multiregion]]:
    return strategies.tuples(planar.multicontours(coordinates),
                             planar.multicontours(coordinates))


multiregions_pairs = coordinates_strategies.flatmap(to_multiregions_pairs)
polygons = coordinates_strategies.flatmap(planar.polygons)


def to_polygons_with_points(coordinates: Strategy[Scalar]
                            ) -> Strategy[Tuple[Polygon, Point]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.points(coordinates))


polygons_with_points = coordinates_strategies.flatmap(to_polygons_with_points)


def to_polygons_with_segments(coordinates: Strategy[Scalar]
                              ) -> Strategy[Tuple[Polygon, Segment]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.segments(coordinates))


polygons_with_segments = (coordinates_strategies
                          .flatmap(to_polygons_with_segments))


def to_polygons_with_multisegments(coordinates: Strategy[Scalar]
                                   ) -> Strategy[Tuple[Polygon, Multisegment]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.multisegments(coordinates))


def polygon_to_polygons_with_multisegments(polygon: Polygon
                                           ) -> Strategy[Tuple[Polygon,
                                                               Multisegment]]:
    return strategies.tuples(strategies.just(polygon),
                             sub_lists(list(to_polygon_edges(polygon)))
                             .map(Multisegment))


polygons_with_multisegments = (
        polygons.flatmap(polygon_to_polygons_with_multisegments)
        | coordinates_strategies.flatmap(to_polygons_with_multisegments))


def to_polygons_with_contours(coordinates: Strategy[Scalar]
                              ) -> Strategy[Tuple[Polygon, Contour]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.contours(coordinates))


polygons_with_contours = (coordinates_strategies
                          .flatmap(to_polygons_with_contours))


def to_polygons_with_multiregions(coordinates: Strategy[Scalar]
                                  ) -> Strategy[Tuple[Polygon, Multiregion]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.multicontours(coordinates))


def polygon_to_polygons_with_multiregions(polygon: Polygon
                                          ) -> Strategy[Tuple[Polygon,
                                                              Multiregion]]:
    return strategies.tuples(strategies.just(polygon),
                             sub_lists(polygon.holes))


polygons_with_multiregions = (coordinates_strategies
                              .flatmap(to_polygons_with_multiregions))
polygons_strategies = coordinates_strategies.map(planar.polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)


def to_multipolygons_with_points(coordinates: Strategy[Scalar]
                                 ) -> Strategy[Tuple[Multipolygon, Point]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.points(coordinates))


multipolygons_with_points = (coordinates_strategies
                             .flatmap(to_multipolygons_with_points))


def to_multipolygons_with_segments(coordinates: Strategy[Scalar]
                                   ) -> Strategy[Tuple[Multipolygon, Segment]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.segments(coordinates))


multipolygons_with_segments = (coordinates_strategies
                               .flatmap(to_multipolygons_with_segments))


def to_multipolygons_with_multisegments(coordinates: Strategy[Scalar]
                                        ) -> Strategy[Tuple[Multipolygon,
                                                            Multisegment]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multisegments(coordinates))


def multipolygon_to_multipolygons_with_multisegments(
        multipolygon: Multipolygon) -> Strategy[Tuple[Multipolygon,
                                                      Multisegment]]:
    edges = list(to_multipolygon_edges(multipolygon))
    return strategies.tuples(strategies.just(multipolygon),
                             sub_lists(edges).map(Multisegment))


multipolygons_with_multisegments = (
        multipolygons.flatmap(multipolygon_to_multipolygons_with_multisegments)
        | coordinates_strategies.flatmap(to_multipolygons_with_multisegments))


def to_multipolygons_with_contours(coordinates: Strategy[Scalar]
                                   ) -> Strategy[Tuple[Multipolygon, Contour]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.contours(coordinates))


multipolygons_with_contours = (coordinates_strategies
                               .flatmap(to_multipolygons_with_contours))


def to_multipolygons_with_multiregions(coordinates: Strategy[Scalar]
                                       ) -> Strategy[Tuple[Multipolygon,
                                                           Multiregion]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multicontours(coordinates))


multipolygons_with_multiregions = (
    coordinates_strategies.flatmap(to_multipolygons_with_multiregions))


def to_multipolygons_with_polygons(coordinates: Strategy[Scalar]
                                   ) -> Strategy[Tuple[Multipolygon, Polygon]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.polygons(coordinates))


multipolygons_with_polygons = (coordinates_strategies
                               .flatmap(to_multipolygons_with_polygons))


def to_multipolygons_pairs(coordinates: Strategy[Scalar]
                           ) -> Strategy[Tuple[Multipolygon, Multipolygon]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multipolygons(coordinates))


multipolygons_pairs = (coordinates_strategies.map(planar.multipolygons)
                       .flatmap(to_pairs))
