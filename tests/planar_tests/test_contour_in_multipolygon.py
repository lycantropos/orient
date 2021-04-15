from typing import Tuple

from ground.base import Relation
from ground.hints import (Contour,
                          Multipolygon)
from hypothesis import given

from orient.planar import (contour_in_multipolygon,
                           contour_in_polygon,
                           point_in_multipolygon,
                           segment_in_multipolygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         multipolygon_pop_left,
                         multipolygon_rotations,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         to_contour_edges)
from . import strategies


@given(strategies.multipolygons_with_contours)
def test_basic(multipolygon_with_contour: Tuple[Multipolygon, Contour]
               ) -> None:
    multipolygon, contour = multipolygon_with_contour

    result = contour_in_multipolygon(contour, multipolygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert all(contour_in_multipolygon(polygon.border, multipolygon)
               is Relation.COMPONENT
               for polygon in multipolygon.polygons)
    assert all(contour_in_multipolygon(hole, multipolygon)
               is Relation.COMPONENT
               for polygon in multipolygon.polygons
               for hole in polygon.holes)


@given(strategies.empty_multipolygons_with_contours)
def test_base(multipolygon_with_contour: Tuple[Multipolygon, Contour]) -> None:
    multipolygon, contour = multipolygon_with_contour

    assert contour_in_multipolygon(contour, multipolygon) is Relation.DISJOINT


@given(strategies.non_empty_multipolygons_with_contours)
def test_step(multipolygon_with_contour: Tuple[Multipolygon, Contour]) -> None:
    multipolygon, contour = multipolygon_with_contour
    first_polygon, rest_multipolygon = multipolygon_pop_left(multipolygon)

    result = contour_in_multipolygon(contour, rest_multipolygon)
    next_result = contour_in_multipolygon(contour, multipolygon)

    relation_with_first_polygon = contour_in_polygon(contour, first_polygon)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_polygon
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_polygon is Relation.TOUCH
                       or result is Relation.TOUCH
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_polygon is Relation.COMPONENT)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_polygon is Relation.CROSS)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_polygon is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_polygon is Relation.WITHIN)


@given(strategies.multipolygons_with_contours)
def test_reversals(multipolygon_with_contour: Tuple[Multipolygon, Contour]
                   ) -> None:
    multipolygon, contour = multipolygon_with_contour

    result = contour_in_multipolygon(contour, multipolygon)

    assert result is contour_in_multipolygon(reverse_contour(contour),
                                             multipolygon)
    assert result is contour_in_multipolygon(
            contour, reverse_multipolygon(multipolygon))
    assert result is contour_in_multipolygon(
            contour, reverse_multipolygon_borders(multipolygon))
    assert result is contour_in_multipolygon(
            contour, reverse_multipolygon_holes(multipolygon))
    assert result is contour_in_multipolygon(
            contour, reverse_multipolygon_holes_contours(multipolygon))
    assert result is contour_in_multipolygon(
            reverse_contour_coordinates(contour),
            reverse_multipolygon_coordinates(multipolygon))


@given(strategies.multipolygons_with_contours)
def test_rotations(multipolygon_with_contour: Tuple[Multipolygon, Contour]
                   ) -> None:
    multipolygon, contour = multipolygon_with_contour

    result = contour_in_multipolygon(contour, multipolygon)

    assert all(result is contour_in_multipolygon(contour, rotated)
               for rotated in multipolygon_rotations(multipolygon))


@given(strategies.multipolygons_with_contours)
def test_connection_with_point_in_multipolygon(multipolygon_with_contour
                                               : Tuple[Multipolygon, Contour]
                                               ) -> None:
    multipolygon, contour = multipolygon_with_contour

    result = contour_in_multipolygon(contour, multipolygon)

    vertices_relations = [point_in_multipolygon(vertex, multipolygon)
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


@given(strategies.multipolygons_with_contours)
def test_connection_with_segment_in_multipolygon(multipolygon_with_contour
                                                 : Tuple[Multipolygon, Contour]
                                                 ) -> None:
    multipolygon, contour = multipolygon_with_contour

    result = contour_in_multipolygon(contour, multipolygon)

    edges_relations = [segment_in_multipolygon(edge, multipolygon)
                       for edge in to_contour_edges(contour)]
    assert equivalence(result is Relation.DISJOINT,
                       all(edge_relation is Relation.DISJOINT
                           for edge_relation in edges_relations))
    assert equivalence(result is Relation.TOUCH,
                       all(edge_relation is not Relation.CROSS
                           and edge_relation is not Relation.ENCLOSED
                           and edge_relation is not Relation.WITHIN
                           for edge_relation in edges_relations)
                       and any(edge_relation is Relation.TOUCH
                               for edge_relation in edges_relations))
    assert equivalence(result is Relation.CROSS,
                       any(edge_relation is Relation.CROSS
                           for edge_relation in edges_relations)
                       or any(edge_relation is Relation.TOUCH
                              or edge_relation is Relation.DISJOINT
                              for edge_relation in edges_relations)
                       and any(edge_relation is Relation.ENCLOSED
                               or edge_relation is Relation.WITHIN
                               for edge_relation in edges_relations))
    assert equivalence(result is Relation.COMPONENT,
                       all(edge_relation is Relation.COMPONENT
                           for edge_relation in edges_relations))
    assert equivalence(result is Relation.ENCLOSED,
                       all(edge_relation is Relation.COMPONENT
                           or edge_relation is Relation.ENCLOSED
                           or edge_relation is Relation.WITHIN
                           for edge_relation in edges_relations)
                       and any(edge_relation is Relation.COMPONENT
                               or edge_relation is Relation.ENCLOSED
                               for edge_relation in edges_relations)
                       and any(edge_relation is Relation.ENCLOSED
                               or edge_relation is Relation.WITHIN
                               for edge_relation in edges_relations))
    assert equivalence(result is Relation.WITHIN,
                       all(edge_relation is Relation.WITHIN
                           for edge_relation in edges_relations))
