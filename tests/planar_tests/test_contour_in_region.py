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
                         reverse_contour_coordinates,
                         to_contour_segments)
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
    assert result is contour_in_region(reverse_contour_coordinates(contour),
                                       reverse_contour_coordinates(region))


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

    contour_segments_relations = [segment_in_region(segment, region)
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
