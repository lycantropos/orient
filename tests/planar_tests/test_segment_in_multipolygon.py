from typing import Tuple

from hypothesis import given

from orient.hints import (Multipolygon,
                          Segment)
from orient.planar import (Relation,
                           point_in_multipolygon,
                           segment_in_multipolygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_segment,
                         rotations)
from . import strategies


@given(strategies.multipolygons_with_segments)
def test_basic(multipolygon_with_segment: Tuple[Multipolygon, Segment]
               ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.empty_multipolygons_with_segments)
def test_base(multipolygon_with_polygon: Tuple[Multipolygon, Segment]) -> None:
    multipolygon, segment = multipolygon_with_polygon

    assert segment_in_multipolygon(segment, multipolygon) is Relation.DISJOINT


@given(strategies.non_empty_multipolygons_with_segments)
def test_step(multipolygon_with_polygon: Tuple[Multipolygon, Segment]) -> None:
    multipolygon, segment = multipolygon_with_polygon
    first_polygon, *rest_multipolygon = multipolygon

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


@given(strategies.multipolygons_with_segments)
def test_rotations(multipolygon_with_segment: Tuple[Multipolygon, Segment]
                   ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    assert all(result is segment_in_multipolygon(segment, rotated)
               for rotated in rotations(multipolygon))


@given(strategies.multipolygons_with_segments)
def test_connection_with_point_in_multipolygon(multipolygon_with_segment
                                               : Tuple[Multipolygon, Segment]
                                               ) -> None:
    multipolygon, segment = multipolygon_with_segment

    result = segment_in_multipolygon(segment, multipolygon)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_multipolygon(start, multipolygon)
                       is point_in_multipolygon(end, multipolygon)
                       is Relation.DISJOINT)
