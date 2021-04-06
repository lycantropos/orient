from typing import Tuple

from ground.base import Relation
from ground.hints import Contour
from hypothesis import given

from orient.hints import Region
from orient.planar import (contour_in_region,
                           point_in_region,
                           segment_in_region)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         contour_rotations,
                         equivalence,
                         implication,
                         reverse_contour,
                         to_contour_edges)
from . import strategies


@given(strategies.contours_pairs)
def test_basic(contour_with_region: Tuple[Contour, Region]) -> None:
    contour, region = contour_with_region

    result = contour_in_region(contour, region)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_region(contour, contour) is Relation.COMPONENT


@given(strategies.contours_pairs)
def test_reversals(region_with_contour: Tuple[Region, Contour]) -> None:
    region, contour = region_with_contour

    result = contour_in_region(contour, region)

    assert result is contour_in_region(reverse_contour(contour), region)
    assert result is contour_in_region(contour, reverse_contour(region))


@given(strategies.contours_pairs)
def test_rotations(region_with_contour: Tuple[Region, Contour]) -> None:
    region, contour = region_with_contour

    result = contour_in_region(contour, region)

    assert all(result is contour_in_region(rotated, region)
               for rotated in contour_rotations(contour))
    assert all(result is contour_in_region(contour, rotated)
               for rotated in contour_rotations(region))


@given(strategies.contours_pairs)
def test_connection_with_point_in_region(region_with_contour
                                         : Tuple[Region, Contour]) -> None:
    region, contour = region_with_contour

    result = contour_in_region(contour, region)

    vertices_relations = [point_in_region(vertex, region)
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


@given(strategies.contours_pairs)
def test_connection_with_segment_in_region(region_with_contour
                                           : Tuple[Region, Contour]) -> None:
    region, contour = region_with_contour

    result = contour_in_region(contour, region)

    edges_relations = [segment_in_region(edge, region)
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
