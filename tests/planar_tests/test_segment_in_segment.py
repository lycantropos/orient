from typing import Tuple

from ground.base import Relation
from ground.hints import Segment
from hypothesis import given

from orient.planar import segment_in_segment
from tests.utils import (ASYMMETRIC_LINEAR_RELATIONS,
                         SAME_LINEAR_RELATIONS,
                         SYMMETRIC_SAME_LINEAR_RELATIONS,
                         equivalence,
                         reverse_segment)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.segments)
def test_self(segment: Segment) -> None:
    assert segment_in_segment(segment, segment) is Relation.EQUAL


@given(strategies.segments_pairs)
def test_relations(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    complement = segment_in_segment(right_segment, left_segment)
    assert equivalence(result is complement,
                       result in SYMMETRIC_SAME_LINEAR_RELATIONS)
    assert equivalence(result is not complement,
                       result.complement is complement
                       and result in ASYMMETRIC_LINEAR_RELATIONS
                       and complement in ASYMMETRIC_LINEAR_RELATIONS)


@given(strategies.segments_pairs)
def test_reversals(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    assert result is segment_in_segment(reverse_segment(left_segment),
                                        right_segment)
    assert result is segment_in_segment(left_segment,
                                        reverse_segment(right_segment))
