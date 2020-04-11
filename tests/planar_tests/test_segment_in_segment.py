from typing import Tuple

from hypothesis import given

from orient.hints import Segment
from orient.planar import (Relation,
                           segment_in_segment)
from tests.utils import (equivalence,
                         reverse_segment)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    assert isinstance(result, Relation)


@given(strategies.segments)
def test_self(segment: Segment) -> None:
    assert segment_in_segment(segment, segment) is Relation.EQUAL


@given(strategies.segments_pairs)
def test_symmetric_relations(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    complement = segment_in_segment(right_segment, left_segment)
    assert equivalence(result is complement,
                       result in (Relation.DISJOINT, Relation.TOUCH,
                                  Relation.CROSS, Relation.OVERLAP,
                                  Relation.EQUAL))


@given(strategies.segments_pairs)
def test_asymmetric_relations(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    complement = segment_in_segment(right_segment, left_segment)
    assert equivalence(result is Relation.COMPOSITE,
                       complement is Relation.COMPONENT)


@given(strategies.segments_pairs)
def test_reversed(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    result = segment_in_segment(left_segment, right_segment)

    assert result is segment_in_segment(reverse_segment(left_segment),
                                        right_segment)
    assert result is segment_in_segment(left_segment,
                                        reverse_segment(right_segment))
