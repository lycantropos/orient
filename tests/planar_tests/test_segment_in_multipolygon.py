from typing import Tuple

from ground.base import Relation
from ground.hints import (Multipolygon,
                          Segment)
from hypothesis import given

from orient.planar import (point_in_multipolygon,
                           segment_in_multipolygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         multipolygon_pop_left,
                         multipolygon_rotations,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.multipolygons_with_segments)
def test_basic(multipolygon_with_segment: Tuple[Multipolygon, Segment]
               ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.multipolygons_with_segments)
def test_step(multipolygon_with_polygon: Tuple[Multipolygon, Segment]) -> None:
    multipolygon, segment = multipolygon_with_polygon
    first_polygon, rest_multipolygon = multipolygon_pop_left(multipolygon)

    result = segment_in_multipolygon(segment, rest_multipolygon)
    next_result = segment_in_multipolygon(segment, multipolygon)

    relation_with_first_polygon = segment_in_polygon(segment, first_polygon)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       and relation_with_first_polygon is Relation.DISJOINT)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_polygon is Relation.WITHIN)
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_polygon is Relation.COMPONENT)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_polygon is Relation.CROSS)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_polygon is Relation.DISJOINT
                            or relation_with_first_polygon is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_polygon is Relation.TOUCH)


@given(strategies.multipolygons_with_segments)
def test_reversals(multipolygon_with_segment: Tuple[Multipolygon, Segment]
                   ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    assert result is segment_in_multipolygon(reverse_segment(segment),
                                             multipolygon)
    assert result is segment_in_multipolygon(segment,
                                             reverse_multipolygon(
                                                     multipolygon))
    assert result is segment_in_multipolygon(
            segment, reverse_multipolygon_borders(multipolygon))
    assert result is segment_in_multipolygon(
            segment, reverse_multipolygon_holes(multipolygon))
    assert result is segment_in_multipolygon(
            segment, reverse_multipolygon_holes_contours(multipolygon))
    assert result is segment_in_multipolygon(
            reverse_segment_coordinates(segment),
            reverse_multipolygon_coordinates(multipolygon))


@given(strategies.multipolygons_with_segments)
def test_rotations(multipolygon_with_segment: Tuple[Multipolygon, Segment]
                   ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    assert all(result is segment_in_multipolygon(segment, rotated)
               for rotated in multipolygon_rotations(multipolygon))


@given(strategies.multipolygons_with_segments)
def test_connection_with_point_in_multipolygon(multipolygon_with_segment
                                               : Tuple[Multipolygon, Segment]
                                               ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    assert implication(result is Relation.DISJOINT,
                       point_in_multipolygon(segment.start, multipolygon)
                       is point_in_multipolygon(segment.end, multipolygon)
                       is Relation.DISJOINT)
