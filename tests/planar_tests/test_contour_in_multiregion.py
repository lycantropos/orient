from typing import Tuple

from hypothesis import given

from orient.core.contour import to_segments
from orient.hints import (Contour,
                          Multiregion)
from orient.planar import (Relation,
                           contour_in_multiregion,
                           contour_in_region,
                           point_in_multiregion,
                           segment_in_multiregion)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_multicontour,
                         reverse_multicontour_contours,
                         rotations)
from . import strategies


@given(strategies.multicontours_with_contours)
def test_basic(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_multiregion(contour, [contour]) is Relation.COMPONENT


@given(strategies.multicontours)
def test_elements(multiregion: Multiregion) -> None:
    assert all(contour_in_multiregion(element, multiregion)
               is Relation.COMPONENT
               for element in multiregion)


@given(strategies.empty_multicontours_with_contours)
def test_base(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    assert contour_in_multiregion(contour, multiregion) is Relation.DISJOINT


@given(strategies.non_empty_multicontours_with_contours)
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


@given(strategies.multicontours_with_contours)
def test_reversals(multiregion_with_contour: Tuple[Multiregion, Contour]
                   ) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert result is contour_in_multiregion(reverse_contour(contour),
                                            multiregion)
    assert result is contour_in_multiregion(contour,
                                            reverse_multicontour(multiregion))
    assert result is contour_in_multiregion(
            contour, reverse_multicontour_contours(multiregion))


@given(strategies.multicontours_with_contours)
def test_rotations(multiregion_with_contour: Tuple[Multiregion, Contour]
                   ) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert all(result is contour_in_multiregion(contour, rotated)
               for rotated in rotations(multiregion))


@given(strategies.multicontours_with_contours)
def test_connection_with_point_in_multiregion(
        multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    vertices_relations = [point_in_multiregion(vertex, multiregion)
                          for vertex in contour]
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


@given(strategies.multicontours_with_contours)
def test_connection_with_segment_in_multiregion(
        multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    edges_relations = [segment_in_multiregion(edge, multiregion)
                       for edge in to_segments(contour)]
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
