from typing import Tuple

from hypothesis import given

from orient.hints import (Multiregion,
                          Segment)
from orient.planar import (Relation,
                           point_in_multiregion,
                           segment_in_multiregion,
                           segment_in_region)
from tests.utils import (equivalence,
                         implication,
                         reverse_contour,
                         reverse_multicontour,
                         reverse_multicontour_contours,
                         reverse_segment,
                         rotations)
from . import strategies


@given(strategies.multicontours_with_segments)
def test_basic(multiregion_with_segment: Tuple[Multiregion, Segment]) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert isinstance(result, Relation)


@given(strategies.multicontours_with_segments)
def test_outside(multiregion_with_segment: Tuple[Multiregion, Segment]
                 ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_multiregion(start, multiregion)
                       is point_in_multiregion(end, multiregion)
                       is Relation.DISJOINT)


@given(strategies.empty_multicontours_with_segments)
def test_base(multiregion_with_region: Tuple[Multiregion, Segment]) -> None:
    multiregion, segment = multiregion_with_region

    assert segment_in_multiregion(segment, multiregion) is Relation.DISJOINT


@given(strategies.non_empty_multicontours_with_segments)
def test_step(multiregion_with_region: Tuple[Multiregion, Segment]) -> None:
    multiregion, segment = multiregion_with_region
    first_contour, *rest_multiregion = multiregion

    result = segment_in_multiregion(segment, rest_multiregion)
    next_result = segment_in_multiregion(segment, multiregion)

    relation_with_first_contour = segment_in_region(segment, first_contour)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       and relation_with_first_contour is Relation.DISJOINT)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_contour is Relation.WITHIN)
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_contour is Relation.COMPONENT)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_contour is Relation.CROSS)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_contour is Relation.DISJOINT
                            or relation_with_first_contour is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_contour is Relation.TOUCH)


@given(strategies.multicontours_with_segments)
def test_reversed(multiregion_with_segment: Tuple[Multiregion, Segment]
                  ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert result is segment_in_multiregion(segment,
                                            reverse_multicontour(multiregion))


@given(strategies.multicontours_with_segments)
def test_reversed_segment(multiregion_with_segment: Tuple[Multiregion, Segment]
                          ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert result is segment_in_multiregion(reverse_segment(segment),
                                            multiregion)


@given(strategies.multicontours_with_segments)
def test_reversed_regions(multiregion_with_segment: Tuple[Multiregion, Segment]
                          ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert result is segment_in_multiregion(
            segment, reverse_multicontour_contours(multiregion))
    assert result is segment_in_multiregion(reverse_contour(segment),
                                            multiregion)


@given(strategies.multicontours_with_segments)
def test_rotations(multiregion_with_segment: Tuple[Multiregion, Segment]
                   ) -> None:
    multiregion, segment = multiregion_with_segment

    result = segment_in_multiregion(segment, multiregion)

    assert all(result is segment_in_multiregion(segment, rotated)
               for rotated in rotations(multiregion))
