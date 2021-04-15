from itertools import chain
from operator import getitem
from typing import (Any,
                    Callable,
                    Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.base import (Orientation,
                         Relation,
                         get_context)
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from orient.core.utils import flatten
from orient.hints import Multiregion

Domain = TypeVar('Domain')
Key = Callable[[Domain], Any]
Strategy = SearchStrategy
context = get_context()
Point = context.point_cls
Segment = context.segment_cls
Multisegment = context.multisegment_cls
Contour = context.contour_cls
Polygon = context.polygon_cls
Multipolygon = context.multipolygon_cls

PRIMITIVE_LINEAR_RELATIONS = Relation.DISJOINT, Relation.COMPONENT
PRIMITIVE_COMPOUND_RELATIONS = PRIMITIVE_LINEAR_RELATIONS + (Relation.WITHIN,)
SYMMETRIC_LINEAR_RELATIONS = (Relation.DISJOINT, Relation.TOUCH,
                              Relation.CROSS, Relation.OVERLAP)
ASYMMETRIC_LINEAR_RELATIONS = Relation.COMPONENT, Relation.COMPOSITE
LINEAR_RELATIONS = SYMMETRIC_LINEAR_RELATIONS + ASYMMETRIC_LINEAR_RELATIONS
SYMMETRIC_SAME_LINEAR_RELATIONS = (SYMMETRIC_LINEAR_RELATIONS
                                   + (Relation.EQUAL,))
SAME_LINEAR_RELATIONS = (SYMMETRIC_SAME_LINEAR_RELATIONS
                         + ASYMMETRIC_LINEAR_RELATIONS)
LINEAR_COMPOUND_RELATIONS = (Relation.DISJOINT, Relation.TOUCH, Relation.CROSS,
                             Relation.COMPONENT, Relation.ENCLOSED,
                             Relation.WITHIN)
SYMMETRIC_COMPOUND_RELATIONS = (Relation.DISJOINT, Relation.TOUCH,
                                Relation.OVERLAP, Relation.EQUAL)
ASYMMETRIC_UNIFORM_COMPOUND_RELATIONS = (Relation.COVER, Relation.ENCLOSES,
                                         Relation.ENCLOSED, Relation.WITHIN)
UNIFORM_COMPOUND_RELATIONS = (SYMMETRIC_COMPOUND_RELATIONS
                              + ASYMMETRIC_UNIFORM_COMPOUND_RELATIONS)
ASYMMETRIC_MULTIPART_COMPOUND_RELATIONS = (
        ASYMMETRIC_UNIFORM_COMPOUND_RELATIONS + (Relation.COMPOSITE,
                                                 Relation.COMPONENT))
MULTIPART_COMPOUND_RELATIONS = (SYMMETRIC_COMPOUND_RELATIONS
                                + ASYMMETRIC_MULTIPART_COMPOUND_RELATIONS)


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def equivalence(left: bool, right: bool) -> bool:
    return left is right


def are_contours_equal(left: Contour, right: Contour) -> bool:
    return _normalize_region(left) == _normalize_region(right)


def are_polygons_equivalent(left: Polygon, right: Polygon) -> bool:
    return (are_contours_equal(left.border, right.border)
            and (_normalize_multiregion(left.holes)
                 == _normalize_multiregion(right.holes)))


are_regions_equal = are_contours_equal


def contour_rotations(contour: Contour) -> Iterable[Contour]:
    for vertices in sequence_rotations(contour.vertices):
        yield Contour(vertices)


def contour_to_multisegment(contour: Contour) -> Multisegment:
    return Multisegment(list(to_contour_edges(contour)))


def multipolygon_pop_left(multipolygon: Multipolygon
                          ) -> Tuple[Polygon, Multipolygon]:
    first_polygon, *rest_polygons = multipolygon.polygons
    return first_polygon, Multipolygon(rest_polygons)


def multipolygon_rotations(multipolygon: Multipolygon
                           ) -> Iterable[Multipolygon]:
    for polygons in sequence_rotations(multipolygon.polygons):
        yield Multipolygon(polygons)


def multipolygon_to_multisegment(multipolygon: Multipolygon) -> Multisegment:
    return Multisegment(list(to_multipolygon_edges(multipolygon)))


def multiregion_to_multisegment(multiregion: Multiregion) -> Multisegment:
    return Multisegment(list(to_multiregion_edges(multiregion)))


def multisegment_pop_left(multisegment: Multisegment
                          ) -> Tuple[Segment, Multisegment]:
    first_segment, *rest_segments = multisegment.segments
    return first_segment, Multisegment(rest_segments)


def multisegment_rotations(multisegment: Multisegment
                           ) -> Iterable[Multisegment]:
    for segments in sequence_rotations(multisegment.segments):
        yield Multisegment(segments)


orientation = context.angle_orientation


def polygon_to_multipolygon(polygon: Polygon) -> Multipolygon:
    return Multipolygon([polygon])


def polygon_to_multisegment(polygon: Polygon) -> Multisegment:
    return Multisegment(list(to_polygon_edges(polygon)))


region_rotations = contour_rotations


def reverse_contour(contour: Contour) -> Contour:
    return Contour(contour.vertices[::-1])


def reverse_contour_coordinates(contour: Contour) -> Contour:
    return Contour([reverse_point_coordinates(vertex)
                    for vertex in contour.vertices])


def reverse_segment(segment: Segment) -> Segment:
    return Segment(segment.end, segment.start)


def reverse_segment_coordinates(segment: Segment) -> Segment:
    return Segment(reverse_point_coordinates(segment.start),
                   reverse_point_coordinates(segment.end))


def reverse_point_coordinates(point: Point) -> Point:
    return Point(point.y, point.x)


region_to_multisegment = contour_to_multisegment


def reverse_polygon_border(polygon: Polygon) -> Polygon:
    return Polygon(reverse_contour(polygon.border), polygon.holes)


def reverse_polygon_coordinates(polygon: Polygon) -> Polygon:
    return Polygon(reverse_contour_coordinates(polygon.border),
                   [reverse_contour_coordinates(hole)
                    for hole in polygon.holes])


def reverse_polygon_holes(polygon: Polygon) -> Polygon:
    return Polygon(polygon.border, reverse_multiregion(polygon.holes))


def reverse_polygon_holes_contours(polygon: Polygon) -> Polygon:
    return Polygon(polygon.border, reverse_multiregion_regions(polygon.holes))


def reverse_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    return Multipolygon(multipolygon.polygons[::-1])


def reverse_multipolygon_borders(multipolygon: Multipolygon) -> Multipolygon:
    return Multipolygon([Polygon(reverse_contour(polygon.border),
                                 polygon.holes)
                         for polygon in multipolygon.polygons])


def reverse_multipolygon_holes(multipolygon: Multipolygon) -> Multipolygon:
    return Multipolygon([Polygon(polygon.border,
                                 reverse_multiregion(polygon.holes))
                         for polygon in multipolygon.polygons])


def reverse_multipolygon_holes_contours(multipolygon: Multipolygon
                                        ) -> Multipolygon:
    return Multipolygon([Polygon(polygon.border,
                                 reverse_multiregion_regions(polygon.holes))
                         for polygon in multipolygon.polygons])


def reverse_multiregion(multiregion: Multiregion) -> Multiregion:
    return multiregion[::-1]


def reverse_multiregion_regions(multiregion: Multiregion) -> Multiregion:
    return [reverse_contour(contour) for contour in multiregion]


def reverse_multiregion_coordinates(multiregion: Multiregion) -> Multiregion:
    return [reverse_contour_coordinates(contour) for contour in multiregion]


def reverse_multisegment(multisegment: Multisegment) -> Multisegment:
    return Multisegment(multisegment.segments[::-1])


def reverse_multisegment_coordinates(multisegment: Multisegment
                                     ) -> Multisegment:
    return Multisegment([reverse_segment_coordinates(segment)
                         for segment in multisegment.segments])


def rotate_sequence(sequence: Domain, offset: int) -> Domain:
    return (sequence[offset:] + sequence[:offset]
            if offset and sequence
            else sequence)


def segment_to_multisegment(segment: Segment) -> Multisegment:
    return Multisegment([segment])


def sequence_rotations(sequence: Domain) -> Iterable[Domain]:
    yield sequence
    for offset in range(1, len(sequence)):
        yield rotate_sequence(sequence, offset)


def sub_lists(sequence: Sequence[Domain]) -> Strategy[List[Domain]]:
    return strategies.builds(getitem,
                             strategies.permutations(sequence),
                             strategies.slices(max(len(sequence), 1)))


def to_contour_convex_hull(contour: Contour) -> Contour:
    return Contour(context.points_convex_hull(contour.vertices))


def to_contour_edges(contour: Contour) -> Iterable[Segment]:
    vertices = contour.vertices
    return (Segment(vertices[index - 1], vertices[index])
            for index in range(len(vertices)))


def to_contour_separators(contour: Contour) -> Iterable[Segment]:
    vertices = contour.vertices
    return (Segment(vertices[index], vertices[next_index])
            for index in range(len(vertices))
            for next_index in chain(range(int(index == len(vertices) - 1),
                                          index - 1),
                                    range(index + 2,
                                          min(len(vertices) + index - 1,
                                              len(vertices)))))


def to_multipolygon_edges(multipolygon: Multipolygon) -> Iterable[Segment]:
    return flatten(map(to_polygon_edges, multipolygon.polygons))


def to_multipolygon_vertices(multipolygon: Multipolygon) -> Iterable[Point]:
    return flatten(map(to_polygon_vertices, multipolygon.polygons))


def to_multiregion_edges(multiregion: Multiregion) -> Iterable[Segment]:
    return flatten(map(to_region_edges, multiregion))


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def to_polygon_convex_hull(polygon: Polygon) -> Polygon:
    return Polygon(to_contour_convex_hull(polygon.border), [])


def to_polygon_edges(polygon: Polygon) -> Iterable[Segment]:
    return chain(to_contour_edges(polygon.border),
                 flatten(map(to_contour_edges, polygon.holes)))


def to_polygon_vertices(polygon: Polygon) -> Iterable[Point]:
    return chain(polygon.border.vertices,
                 flatten(hole.vertices for hole in polygon.holes))


def to_polygon_with_convex_border(polygon: Polygon) -> Polygon:
    return Polygon(to_contour_convex_hull(polygon.border),
                   polygon.holes)


to_region_convex_hull = to_contour_convex_hull
to_region_edges = to_contour_edges


def to_solid_polygon(polygon: Polygon) -> Polygon:
    return Polygon(polygon.border, [])


def to_triplets(strategy: Strategy[Domain]
                ) -> Strategy[Tuple[Domain, Domain, Domain]]:
    return strategies.tuples(strategy, strategy, strategy)


def _normalize_multiregion(multiregion: Multiregion):
    return sorted([_normalize_region(hole) for hole in multiregion],
                  key=lambda region: region.vertices[0])


def _normalize_region(contour: Contour) -> Contour:
    vertices = contour.vertices
    return Contour(_to_counterclockwise_vertices(
            rotate_sequence(vertices, min(range(len(vertices)),
                                          key=vertices.__getitem__))))


def _to_counterclockwise_vertices(vertices: Sequence[Point]
                                  ) -> Sequence[Point]:
    if _to_first_angle_orientation(vertices) is not Orientation.CLOCKWISE:
        vertices = vertices[:1] + vertices[1:][::-1]
    return vertices


def _to_first_angle_orientation(vertices: Sequence[Point]) -> Orientation:
    return context.angle_orientation(vertices[0], vertices[-1], vertices[1])
