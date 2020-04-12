from functools import partial
from typing import (Optional,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from orient.hints import (Contour,
                          Coordinate,
                          Multicontour,
                          Point,
                          Polygon,
                          Segment)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
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
contours = coordinates_strategies.flatmap(planar.contours)


def to_contours_with_segments(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Contour, Segment]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.segments(coordinates))


contours_with_segments = (coordinates_strategies
                          .flatmap(to_contours_with_segments))
multicontours = coordinates_strategies.flatmap(planar.multicontours)


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
empty_multicontours_with_points = strategies.tuples(strategies.builds(list),
                                                    points)
non_empty_multicontours_with_points = coordinates_strategies.flatmap(
        partial(to_multicontours_with_points,
                min_size=1))


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
empty_multicontours_with_contours = strategies.tuples(strategies.builds(list),
                                                      contours)
non_empty_multicontours_with_contours = coordinates_strategies.flatmap(
        partial(to_multicontours_with_contours,
                min_size=1))


def to_contours_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Contour, Point]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.points(coordinates))


contours_with_points = coordinates_strategies.flatmap(to_contours_with_points)


def to_contours_with_polygons(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Contour, Polygon]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.polygons(coordinates))


contours_with_polygons = (coordinates_strategies
                          .flatmap(to_contours_with_polygons))
contours_strategies = coordinates_strategies.map(planar.contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)


def to_polygons_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Polygon, Point]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.points(coordinates))


polygons_with_points = coordinates_strategies.flatmap(to_polygons_with_points)
polygons = coordinates_strategies.flatmap(planar.polygons)


def to_polygons_with_segments(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Polygon, Segment]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.segments(coordinates))


polygons_with_segments = (coordinates_strategies
                          .flatmap(to_polygons_with_segments))
polygons_strategies = coordinates_strategies.map(planar.polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
