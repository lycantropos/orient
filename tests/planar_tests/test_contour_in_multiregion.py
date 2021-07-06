from typing import Tuple

from ground.base import (Location,
                         Relation)
from ground.hints import Contour
from hypothesis import given

from orient.hints import Multiregion
from orient.planar import (contour_in_multiregion,
                           contour_in_region,
                           point_in_multiregion,
                           segment_in_multiregion)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_multiregion_regions,
                         sequence_rotations,
                         to_contour_segments)
from . import strategies


@given(strategies.multiregions_with_contours)
def test_basic(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.multiregions)
def test_self(multiregion: Multiregion) -> None:
    assert all(contour_in_multiregion(region, multiregion)
               is Relation.COMPONENT
               for region in multiregion)


@given(strategies.size_three_or_more_multiregions_with_contours)
def test_step(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour
    first_region, *rest_multiregion = multiregion

    result = contour_in_multiregion(contour, rest_multiregion)
    next_result = contour_in_multiregion(contour, multiregion)

    relation_with_first_region = contour_in_region(contour, first_region)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_region
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_region is Relation.TOUCH
                       or result is Relation.TOUCH
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_region is Relation.COMPONENT)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_region is Relation.CROSS)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_region is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_region is Relation.WITHIN)


@given(strategies.multiregions_with_contours)
def test_reversals(multiregion_with_contour: Tuple[Multiregion, Contour]
                   ) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert result is contour_in_multiregion(reverse_contour(contour),
                                            multiregion)
    assert result is contour_in_multiregion(contour,
                                            reverse_multiregion(multiregion))
    assert result is contour_in_multiregion(
            contour, reverse_multiregion_regions(multiregion))
    assert result is contour_in_multiregion(
            reverse_contour_coordinates(contour),
            reverse_multiregion_coordinates(multiregion))


@given(strategies.multiregions_with_contours)
def test_rotations(multiregion_with_contour: Tuple[Multiregion, Contour]
                   ) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert all(result is contour_in_multiregion(contour, rotated)
               for rotated in sequence_rotations(multiregion))


@given(strategies.multiregions_with_contours)
def test_connection_with_point_in_multiregion(
        multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    vertices_relations = [point_in_multiregion(vertex, multiregion)
                          for vertex in contour.vertices]
    assert implication(result is Relation.DISJOINT,
                       all(vertex_location is Location.EXTERIOR
                           for vertex_location in vertices_relations))
    assert implication(result is Relation.TOUCH,
                       all(vertex_location is not Location.INTERIOR
                           for vertex_location in vertices_relations))
    assert implication(result is Relation.COMPONENT,
                       all(vertex_location is Location.BOUNDARY
                           for vertex_location in vertices_relations))
    assert implication(result is Relation.ENCLOSED,
                       all(vertex_location is not Location.EXTERIOR
                           for vertex_location in vertices_relations))
    assert implication(result is Relation.WITHIN,
                       all(vertex_location is Location.INTERIOR
                           for vertex_location in vertices_relations))
    assert implication(all(vertex_location is Location.EXTERIOR
                           for vertex_location in vertices_relations),
                       result is Relation.DISJOINT
                       or result is Relation.TOUCH
                       or result is Relation.CROSS)
    assert implication(all(vertex_location is Location.INTERIOR
                           for vertex_location in vertices_relations),
                       result is Relation.CROSS
                       or result is Relation.ENCLOSED
                       or result is Relation.WITHIN)
    assert implication(any(vertex_location is Location.EXTERIOR
                           for vertex_location in vertices_relations)
                       and any(vertex_location is Location.INTERIOR
                               for vertex_location in vertices_relations),
                       result is Relation.CROSS)


@given(strategies.multiregions_with_contours)
def test_connection_with_segment_in_multiregion(
        multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    contour_segments_relations = [segment_in_multiregion(segment, multiregion)
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
