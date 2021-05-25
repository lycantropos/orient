from typing import Tuple

from ground.base import Relation
from ground.hints import (Contour,
                          Polygon)
from hypothesis import given

from orient.planar import (contour_in_polygon,
                           point_in_polygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         contour_rotations,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         to_contour_segments)
from . import strategies


@given(strategies.polygons_with_contours)
def test_basic(polygon_with_contour: Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert contour_in_polygon(polygon.border, polygon) is Relation.COMPONENT
    assert all(contour_in_polygon(hole, polygon) is Relation.COMPONENT
               for hole in polygon.holes)


@given(strategies.polygons_with_contours)
def test_reversals(polygon_with_contour: Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    assert result is contour_in_polygon(reverse_contour(contour),
                                        polygon)
    assert result is contour_in_polygon(contour,
                                        reverse_polygon_border(polygon))
    assert result is contour_in_polygon(contour,
                                        reverse_polygon_holes(polygon))
    assert result is contour_in_polygon(
            contour, reverse_polygon_holes_contours(polygon))
    assert result is contour_in_polygon(reverse_contour_coordinates(contour),
                                        reverse_polygon_coordinates(polygon))


@given(strategies.polygons_with_contours)
def test_rotations(polygon_with_contour: Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    assert all(result is contour_in_polygon(rotated, polygon)
               for rotated in contour_rotations(contour))


@given(strategies.polygons_with_contours)
def test_connection_with_point_in_polygon(polygon_with_contour
                                          : Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    vertices_relations = [point_in_polygon(vertex, polygon)
                          for vertex in contour.vertices]
    assert implication(result is Relation.DISJOINT,
                       all(vertex_relation is Relation.DISJOINT
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.TOUCH,
                       all(vertex_relation is not Relation.WITHIN
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.COMPONENT,
                       all(vertex_relation is Relation.COMPONENT
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.ENCLOSED,
                       all(vertex_relation is not Relation.DISJOINT
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.WITHIN,
                       all(vertex_relation is Relation.WITHIN
                           for vertex_relation in vertices_relations))
    assert implication(all(vertex_relation is Relation.DISJOINT
                           for vertex_relation in vertices_relations),
                       result is Relation.DISJOINT
                       or result is Relation.TOUCH
                       or result is Relation.CROSS)
    assert implication(all(vertex_relation is Relation.WITHIN
                           for vertex_relation in vertices_relations),
                       result is Relation.CROSS
                       or result is Relation.ENCLOSED
                       or result is Relation.WITHIN)
    assert implication(any(vertex_relation is Relation.DISJOINT
                           for vertex_relation in vertices_relations)
                       and any(vertex_relation is Relation.WITHIN
                               for vertex_relation in vertices_relations),
                       result is Relation.CROSS)


@given(strategies.polygons_with_contours)
def test_connection_with_segment_in_polygon(polygon_with_contour
                                            : Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    contour_segments_relations = [segment_in_polygon(segment, polygon)
                                  for segment in to_contour_segments(contour)]
    assert equivalence(result is Relation.DISJOINT,
                       all(relation is Relation.DISJOINT
                           for relation in contour_segments_relations))
    assert equivalence(result is Relation.TOUCH,
                       all(relation is not Relation.CROSS
                           and relation is not Relation.ENCLOSED
                           and relation is not Relation.WITHIN
                           for relation in contour_segments_relations)
                       and any(relation is Relation.TOUCH
                               for relation in contour_segments_relations))
    assert equivalence(result is Relation.CROSS,
                       any(relation is Relation.CROSS
                           for relation in contour_segments_relations)
                       or any(relation is Relation.TOUCH
                              or relation is Relation.DISJOINT
                              for relation in contour_segments_relations)
                       and any(relation is Relation.ENCLOSED
                               or relation is Relation.WITHIN
                               for relation in contour_segments_relations))
    assert equivalence(result is Relation.COMPONENT,
                       all(relation is Relation.COMPONENT
                           for relation in contour_segments_relations))
    assert equivalence(result is Relation.ENCLOSED,
                       all(relation is Relation.COMPONENT
                           or relation is Relation.ENCLOSED
                           or relation is Relation.WITHIN
                           for relation in contour_segments_relations)
                       and any(relation is Relation.COMPONENT
                               or relation is Relation.ENCLOSED
                               for relation in contour_segments_relations)
                       and any(relation is Relation.ENCLOSED
                               or relation is Relation.WITHIN
                               for relation in contour_segments_relations))
    assert equivalence(result is Relation.WITHIN,
                       all(relation is Relation.WITHIN
                           for relation in contour_segments_relations))
