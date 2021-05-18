from fractions import Fraction
from functools import partial
from typing import (List,
                    Sequence,
                    Tuple)

from ground.hints import Scalar
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import (coordinates_strategies,
                              rational_coordinates_strategies)
from tests.utils import (Multipolygon,
                         Multisegment,
                         Point,
                         Polygon,
                         Segment,
                         Strategy,
                         cleave_in_tuples,
                         left_scale_segment,
                         right_scale_segment,
                         sub_lists,
                         to_multipolygon_edges,
                         to_pairs,
                         to_polygon_edges,
                         to_triplets)

points = coordinates_strategies.flatmap(planar.points)
segments = coordinates_strategies.flatmap(planar.segments)
segments_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(planar.segments,
                                                  planar.points)))
segments_strategies = coordinates_strategies.map(planar.segments)
segments_pairs = segments_strategies.flatmap(to_pairs)
multisegments = coordinates_strategies.flatmap(planar.multisegments)
multisegments_with_points = (coordinates_strategies
                             .flatmap(cleave_in_tuples(planar.multisegments,
                                                       planar.points)))
multisegments_with_segments = (coordinates_strategies
                               .flatmap(cleave_in_tuples(planar.multisegments,
                                                         planar.segments)))
to_size_three_or_more_multisegments = partial(planar.multisegments,
                                              min_size=3)
size_three_or_more_multisegments_with_segments = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multisegments,
                               planar.segments))))


def chop_segment(segment: Segment, parts_count: int) -> Sequence[Segment]:
    assert parts_count > 1
    step_x, step_y = (Fraction(segment.end.x - segment.start.x) / parts_count,
                      Fraction(segment.end.y - segment.start.y) / parts_count)
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
                                           min_size: int = 2,
                                           max_size: int = 100
                                           ) -> Strategy[Tuple[Multisegment,
                                                               Segment]]:
    just_segment = strategies.just(segment)
    partition_sizes = strategies.integers(min_size, max_size)
    scales = strategies.integers(1, 100)
    partitions = strategies.builds(chop_segment, just_segment, partition_sizes)
    return strategies.tuples(
            (strategies.builds(scale_head,
                               strategies.builds(scale_tail, partitions,
                                                 scales),
                               scales)
             .flatmap(strategies.permutations)
             .map(Multisegment)),
            just_segment)


def scale_head(segment_partition: List[Segment],
               scale: Scalar) -> List[Segment]:
    return segment_partition[:-1] + [left_scale_segment(segment_partition[-1],
                                                        scale)]


def scale_tail(segment_partition: List[Segment],
               scale: Scalar) -> List[Segment]:
    return segment_partition[:-1] + [right_scale_segment(segment_partition[-1],
                                                         scale)]


multisegments_with_segments |= (
    (rational_coordinates_strategies.flatmap(planar.segments)
     .flatmap(segment_to_multisegments_with_segments)))
size_three_or_more_multisegments_with_segments |= (
    (rational_coordinates_strategies.flatmap(planar.segments)
     .flatmap(partial(segment_to_multisegments_with_segments,
                      min_size=3))))
multisegments_strategies = coordinates_strategies.map(planar.multisegments)
multisegments_pairs = (coordinates_strategies.map(planar.multisegments)
                       .flatmap(to_pairs))
size_three_or_more_multisegment_with_multisegment = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multisegments,
                               planar.multisegments))))
contours = coordinates_strategies.flatmap(planar.contours)
contours_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(planar.contours,
                                                  planar.points)))
contours_with_segments = (coordinates_strategies
                          .flatmap(cleave_in_tuples(planar.contours,
                                                    planar.segments)))
contours_with_multisegments = (
    coordinates_strategies.flatmap(cleave_in_tuples(planar.contours,
                                                    planar.multisegments)))
contours_with_size_three_or_more_multisegments = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(planar.contours,
                               to_size_three_or_more_multisegments))))
contours_strategies = coordinates_strategies.map(planar.contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)
to_size_three_or_more_multiregions = partial(planar.multicontours,
                                             min_size=3)
multiregions = coordinates_strategies.flatmap(planar.multicontours)
multiregions_with_points = (coordinates_strategies
                            .flatmap(cleave_in_tuples(planar.multicontours,
                                                      planar.points)))
size_three_or_more_multiregions_with_points = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multiregions,
                               planar.points))))
multiregions_with_segments = (coordinates_strategies
                              .flatmap(cleave_in_tuples(planar.multicontours,
                                                        planar.segments)))
size_three_or_more_multiregions_with_segments = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multiregions,
                               planar.segments))))
multiregions_with_multisegments = (
    coordinates_strategies.flatmap(cleave_in_tuples(planar.multicontours,
                                                    planar.multisegments)))
multiregions_with_size_three_or_more_multisegments = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(planar.multicontours,
                               to_size_three_or_more_multisegments))))
multiregions_with_contours = (coordinates_strategies
                              .flatmap(cleave_in_tuples(planar.multicontours,
                                                        planar.contours)))
size_three_or_more_multiregions_with_contours = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multiregions,
                               planar.contours))))
multiregions_pairs = (coordinates_strategies.map(planar.multicontours)
                      .flatmap(to_pairs))
size_three_or_more_multiregion_with_multiregion = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multiregions,
                               planar.multicontours))))
polygons = coordinates_strategies.flatmap(planar.polygons)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(planar.polygons,
                                                  planar.points)))
polygons_with_segments = (coordinates_strategies
                          .flatmap(cleave_in_tuples(planar.polygons,
                                                    planar.segments)))


def polygon_to_polygons_with_multisegments(polygon: Polygon,
                                           *,
                                           min_size: int = 2
                                           ) -> Strategy[Tuple[Polygon,
                                                               Multisegment]]:
    return strategies.tuples(strategies.just(polygon),
                             sub_lists(list(to_polygon_edges(polygon)),
                                       min_size=min_size)
                             .map(Multisegment))


polygons_with_multisegments = (
        polygons.flatmap(polygon_to_polygons_with_multisegments)
        | (coordinates_strategies
           .flatmap(cleave_in_tuples(planar.polygons, planar.multisegments))))
polygons_with_with_size_three_or_more_multisegments = (
        polygons.flatmap(partial(polygon_to_polygons_with_multisegments,
                                 min_size=3))
        | (coordinates_strategies
           .flatmap(cleave_in_tuples(planar.polygons,
                                     partial(planar.multisegments,
                                             min_size=3)))))
polygons_with_contours = (coordinates_strategies
                          .flatmap(cleave_in_tuples(planar.polygons,
                                                    planar.contours)))
polygons_with_multiregions = (coordinates_strategies
                              .flatmap(cleave_in_tuples(planar.polygons,
                                                        planar.multicontours)))
polygons_with_size_three_or_more_multiregions = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(planar.polygons,
                               to_size_three_or_more_multiregions))))
polygons_strategies = coordinates_strategies.map(planar.polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
to_size_three_or_more_multipolygons = partial(planar.multipolygons,
                                              min_size=3)
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)
multipolygons_with_points = (coordinates_strategies
                             .flatmap(cleave_in_tuples(planar.multipolygons,
                                                       planar.points)))
size_three_or_more_multipolygons_with_points = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multipolygons,
                               planar.points))))
multipolygons_with_segments = (coordinates_strategies
                               .flatmap(cleave_in_tuples(planar.multipolygons,
                                                         planar.segments)))
size_three_or_more_multipolygons_with_segments = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multipolygons,
                               planar.segments))))


def multipolygon_to_multipolygons_with_multisegments(
        multipolygon: Multipolygon,
        *,
        min_size: int = 2) -> Strategy[Tuple[Multipolygon, Multisegment]]:
    edges = list(to_multipolygon_edges(multipolygon))
    return strategies.tuples(strategies.just(multipolygon),
                             sub_lists(edges,
                                       min_size=min_size)
                             .map(Multisegment))


multipolygons_with_multisegments = (
        multipolygons.flatmap(multipolygon_to_multipolygons_with_multisegments)
        | (coordinates_strategies
           .flatmap(cleave_in_tuples(planar.multipolygons,
                                     planar.multisegments))))
multipolygons_with_size_three_or_more_multisegments = (
        (multipolygons
         .flatmap(partial(multipolygon_to_multipolygons_with_multisegments,
                          min_size=3)))
        | (coordinates_strategies
           .flatmap(cleave_in_tuples(planar.multipolygons,
                                     to_size_three_or_more_multisegments))))
multipolygons_with_contours = (coordinates_strategies
                               .flatmap(cleave_in_tuples(planar.multipolygons,
                                                         planar.contours)))
size_three_or_more_multipolygons_with_contours = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multipolygons,
                               planar.contours))))
multipolygons_with_multiregions = (
    coordinates_strategies.flatmap(cleave_in_tuples(planar.multipolygons,
                                                    planar.multicontours)))
size_three_or_more_multipolygons_with_multiregions = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multipolygons,
                               planar.multicontours))))
multipolygons_with_polygons = (coordinates_strategies
                               .flatmap(cleave_in_tuples(planar.multipolygons,
                                                         planar.polygons)))
size_three_or_more_multipolygons_with_polygons = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multipolygons,
                               planar.polygons))))
multipolygons_pairs = (coordinates_strategies.map(planar.multipolygons)
                       .flatmap(to_pairs))
size_three_or_more_multipolygons_with_multipolygons = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(to_size_three_or_more_multipolygons,
                               planar.multipolygons))))
