from typing import Tuple

from ground.base import Relation
from ground.hints import Multipolygon
from hypothesis import given

from orient.planar import (multipolygon_in_multipolygon,
                           polygon_in_multipolygon)
from tests.utils import (ASYMMETRIC_MULTIPART_COMPOUND_RELATIONS,
                         MULTIPART_COMPOUND_RELATIONS,
                         SYMMETRIC_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         multipolygon_pop_left,
                         multipolygon_rotations,
                         polygon_to_multipolygon,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: Tuple[Multipolygon, Multipolygon]) -> None:
    multipolygon, multipolygon = multipolygons_pair

    result = multipolygon_in_multipolygon(multipolygon, multipolygon)

    assert isinstance(result, Relation)
    assert result in MULTIPART_COMPOUND_RELATIONS


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert (multipolygon_in_multipolygon(multipolygon, multipolygon)
            is Relation.EQUAL)
    assert all(multipolygon_in_multipolygon(polygon_to_multipolygon(polygon),
                                            multipolygon)
               is Relation.COMPONENT
               for polygon in multipolygon.polygons)


@given(strategies.multipolygons_pairs)
def test_relations(multipolygons_pair: Tuple[Multipolygon, Multipolygon]
                   ) -> None:
    left, right = multipolygons_pair

    result = multipolygon_in_multipolygon(left, right)

    complement = multipolygon_in_multipolygon(right, left)
    assert equivalence(result is complement,
                       result in SYMMETRIC_COMPOUND_RELATIONS)
    assert equivalence(
            result is not complement,
            result.complement is complement
            and result in ASYMMETRIC_MULTIPART_COMPOUND_RELATIONS
            and complement in ASYMMETRIC_MULTIPART_COMPOUND_RELATIONS)


@given(strategies.size_three_or_more_multipolygons_with_multipolygons)
def test_step(multipolygons_pair: Tuple[Multipolygon, Multipolygon]) -> None:
    left, right = multipolygons_pair
    first_polygon, rest_left = multipolygon_pop_left(left)

    result = multipolygon_in_multipolygon(rest_left, right)
    next_result = multipolygon_in_multipolygon(left, right)

    relation_with_first_polygon = polygon_in_multipolygon(first_polygon, right)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_polygon
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_polygon is Relation.TOUCH)
    assert implication(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_polygon is Relation.OVERLAP
                       or (bool(rest_left.polygons)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_polygon is Relation.COMPONENT
                            or relation_with_first_polygon is Relation.ENCLOSED
                            or relation_with_first_polygon is Relation.WITHIN)
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH))
    assert implication(result is Relation.OVERLAP
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH
                            or relation_with_first_polygon is Relation.ENCLOSED
                            or relation_with_first_polygon is Relation.WITHIN)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH
                           or result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and relation_with_first_polygon is Relation.OVERLAP
                       or (bool(rest_left.polygons)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_polygon is Relation.COMPONENT
                            or relation_with_first_polygon is Relation.ENCLOSED
                            or relation_with_first_polygon is Relation.WITHIN)
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH),
                       next_result is Relation.OVERLAP)
    assert equivalence(next_result is Relation.COVER,
                       result is Relation.COVER
                       or relation_with_first_polygon is Relation.COVER)
    assert implication(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       or relation_with_first_polygon is Relation.ENCLOSES
                       or result is Relation.OVERLAP
                       and (relation_with_first_polygon is Relation.COMPONENT
                            or relation_with_first_polygon is Relation.OVERLAP)
                       or result is Relation.COMPONENT
                       and relation_with_first_polygon is Relation.OVERLAP)
    assert implication(result is Relation.ENCLOSES
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_polygon is Relation.ENCLOSES,
                       next_result is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.COMPOSITE,
                       result is Relation.COMPOSITE or result is Relation.EQUAL
                       or (relation_with_first_polygon is Relation.COMPOSITE
                           or bool(rest_left.polygons)
                           and relation_with_first_polygon is Relation.EQUAL))
    assert implication(result is relation_with_first_polygon
                       is Relation.COMPONENT,
                       next_result is Relation.EQUAL
                       or next_result is Relation.COMPONENT)
    assert implication(not rest_left.polygons
                       and relation_with_first_polygon is Relation.EQUAL,
                       next_result is Relation.EQUAL)
    assert implication(not rest_left.polygons
                       and relation_with_first_polygon is Relation.COMPONENT,
                       next_result is Relation.COMPONENT)
    assert equivalence(next_result is Relation.ENCLOSED,
                       (not rest_left.polygons
                        or result is Relation.COMPONENT
                        or result is Relation.ENCLOSED
                        or result is Relation.WITHIN)
                       and relation_with_first_polygon is Relation.ENCLOSED
                       or result is Relation.ENCLOSED
                       and (relation_with_first_polygon is Relation.COMPONENT
                            or relation_with_first_polygon is Relation.WITHIN))
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_left.polygons or result is Relation.WITHIN)
                       and relation_with_first_polygon is Relation.WITHIN)


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: Tuple[Multipolygon, Multipolygon]
                   ) -> None:
    left, right = multipolygons_pair

    result = multipolygon_in_multipolygon(left, right)

    assert result is multipolygon_in_multipolygon(reverse_multipolygon(left),
                                                  right)
    assert result is multipolygon_in_multipolygon(left,
                                                  reverse_multipolygon(right))
    assert result is multipolygon_in_multipolygon(
            reverse_multipolygon_borders(left), right)
    assert result is multipolygon_in_multipolygon(
            left, reverse_multipolygon_borders(right))
    assert result is multipolygon_in_multipolygon(
            reverse_multipolygon_holes(left), right)
    assert result is multipolygon_in_multipolygon(
            left, reverse_multipolygon_holes(right))
    assert result is multipolygon_in_multipolygon(
            reverse_multipolygon_holes_contours(left), right)
    assert result is multipolygon_in_multipolygon(
            left, reverse_multipolygon_holes_contours(right))
    assert result is multipolygon_in_multipolygon(
            reverse_multipolygon_coordinates(left),
            reverse_multipolygon_coordinates(right))


@given(strategies.multipolygons_pairs)
def test_rotations(multipolygons_pair: Tuple[Multipolygon, Multipolygon]
                   ) -> None:
    left, right = multipolygons_pair

    result = multipolygon_in_multipolygon(left, right)

    assert all(result is multipolygon_in_multipolygon(rotated, right)
               for rotated in multipolygon_rotations(left))
    assert all(result is multipolygon_in_multipolygon(left, rotated)
               for rotated in multipolygon_rotations(right))
