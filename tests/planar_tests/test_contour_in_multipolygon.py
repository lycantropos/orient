from typing import Tuple

from ground.base import (Location,
                         Relation)
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
                         to_contour_segments)
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


@given(strategies.size_three_or_more_multipolygons_with_contours)
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

    vertices_locations = [point_in_multipolygon(vertex, multipolygon)
                          for vertex in contour.vertices]
    assert implication(result is Relation.DISJOINT,
                       all(vertex_location is Location.EXTERIOR
                           for vertex_location in vertices_locations))
    assert implication(result is Relation.TOUCH,
                       all(vertex_location is not Location.INTERIOR
                           for vertex_location in vertices_locations))
    assert implication(result is Relation.COMPONENT,
                       all(vertex_location is Location.BOUNDARY
                           for vertex_location in vertices_locations))
    assert implication(result is Relation.ENCLOSED,
                       all(vertex_location is not Location.EXTERIOR
                           for vertex_location in vertices_locations))
    assert implication(result is Relation.WITHIN,
                       all(vertex_location is Location.INTERIOR
                           for vertex_location in vertices_locations))
    assert implication(all(vertex_location is Location.EXTERIOR
                           for vertex_location in vertices_locations),
                       result is Relation.DISJOINT
                       or result is Relation.TOUCH
                       or result is Relation.CROSS)
    assert implication(all(vertex_location is Location.INTERIOR
                           for vertex_location in vertices_locations),
                       result is Relation.CROSS
                       or result is Relation.ENCLOSED
                       or result is Relation.WITHIN)
    assert implication(any(vertex_location is Location.EXTERIOR
                           for vertex_location in vertices_locations)
                       and any(vertex_location is Location.INTERIOR
                               for vertex_location in vertices_locations),
                       result is Relation.CROSS)


@given(strategies.multipolygons_with_contours)
def test_connection_with_segment_in_multipolygon(multipolygon_with_contour
                                                 : Tuple[Multipolygon, Contour]
                                                 ) -> None:
    multipolygon, contour = multipolygon_with_contour

    result = contour_in_multipolygon(contour, multipolygon)

    contour_segments_relations = [segment_in_multipolygon(segment,
                                                          multipolygon)
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
