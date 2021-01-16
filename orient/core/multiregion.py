from typing import Iterable

from ground.base import (Context,
                         Relation)
from ground.hints import (Box,
                          Contour,
                          Multisegment,
                          Point,
                          Segment)

from . import box
from .contour import to_edges_endpoints as contour_to_edges_endpoints
from .events_queue import CompoundEventsQueue
from .hints import (Multiregion,
                    Region,
                    SegmentEndpoints)
from .multisegment import to_segments_endpoints
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .region import (relate_point as relate_point_to_region,
                     relate_segment as relate_segment_to_region,
                     to_oriented_segments as region_to_oriented_segments)


def relate_point(multiregion: Multiregion, point: Point,
                 *,
                 context: Context) -> Relation:
    for region in multiregion:
        relation_with_region = relate_point_to_region(region, point,
                                                      context=context)
        if relation_with_region is not Relation.DISJOINT:
            return relation_with_region
    return Relation.DISJOINT


def relate_segment(multiregion: Multiregion, segment: Segment,
                   *,
                   context: Context) -> Relation:
    return (relate_segment_to_region(multiregion[0], segment,
                                     context=context)
            if len(multiregion) == 1
            else _relate_multisegment(multiregion,
                                      context.multisegment_cls([segment]),
                                      box.from_segment(segment,
                                                       context=context),
                                      context=context))


def relate_multisegment(multiregion: Multiregion,
                        multisegment: Multisegment,
                        *,
                        context: Context) -> Relation:
    return (_relate_multisegment(multiregion, multisegment,
                                 box.from_multisegment(multisegment,
                                                       context=context),
                                 context=context)
            if multisegment.segments and multiregion
            else Relation.DISJOINT)


def _relate_multisegment(multiregion: Multiregion,
                         multisegment: Multisegment,
                         multisegment_bounding_box: Box,
                         *,
                         context: Context) -> Relation:
    disjoint, multiregion_max_x, events_queue = True, None, None
    for region in multiregion:
        region_bounding_box = box.from_contour(region,
                                               context=context)
        if not box.disjoint_with(region_bounding_box,
                                 multisegment_bounding_box):
            if disjoint:
                disjoint = False
                multiregion_max_x = region_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(to_segments_endpoints(multisegment),
                                      from_test=True)
            else:
                multiregion_max_x = max(multiregion_max_x,
                                        region_bounding_box.max_x)
            events_queue.register(
                    region_to_oriented_segments(region,
                                                context=context),
                    from_test=False)
    if disjoint:
        return Relation.DISJOINT
    return process_linear_compound_queue(events_queue,
                                         min(multisegment_bounding_box.max_x,
                                             multiregion_max_x))


def relate_contour(multiregion: Multiregion, contour: Contour,
                   *,
                   context: Context) -> Relation:
    return (_relate_contour(multiregion, contour,
                            box.from_contour(contour,
                                             context=context),
                            context=context)
            if multiregion
            else Relation.DISJOINT)


def _relate_contour(multiregion: Multiregion,
                    contour: Contour,
                    contour_bounding_box: Box,
                    *,
                    context: Context) -> Relation:
    disjoint, multiregion_max_x, events_queue = True, None, None
    for region in multiregion:
        region_bounding_box = box.from_contour(region,
                                               context=context)
        if not box.disjoint_with(region_bounding_box,
                                 contour_bounding_box):
            if disjoint:
                disjoint = False
                multiregion_max_x = region_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(contour_to_edges_endpoints(contour),
                                      from_test=True)
            else:
                multiregion_max_x = max(multiregion_max_x,
                                        region_bounding_box.max_x)
            events_queue.register(region_to_oriented_segments(region,
                                                              context=context),
                                  from_test=False)
    if disjoint:
        return Relation.DISJOINT
    return process_linear_compound_queue(events_queue,
                                         min(contour_bounding_box.max_x,
                                             multiregion_max_x))


def relate_region(multiregion: Multiregion, region: Region,
                  *,
                  context: Context) -> Relation:
    return (_relate_region(multiregion, region,
                           box.from_contour(region,
                                            context=context),
                           context=context)
            if multiregion
            else Relation.DISJOINT)


def _relate_region(goal_regions: Iterable[Region],
                   region: Region,
                   region_bounding_box: Box,
                   *,
                   context: Context) -> Relation:
    all_disjoint, none_disjoint, goal_regions_max_x, events_queue = (
        True, True,
        None, None)
    for goal_region in goal_regions:
        goal_region_bounding_box = box.from_contour(goal_region,
                                                    context=context)
        if box.disjoint_with(region_bounding_box, goal_region_bounding_box):
            if none_disjoint:
                none_disjoint = False
        else:
            if all_disjoint:
                all_disjoint = False
                goal_regions_max_x = goal_region_bounding_box.max_x
                events_queue = CompoundEventsQueue(context)
                events_queue.register(
                        region_to_oriented_segments(region,
                                                    context=context),
                        from_test=True)
            else:
                goal_regions_max_x = max(goal_regions_max_x,
                                         goal_region_bounding_box.max_x)
            events_queue.register(region_to_oriented_segments(goal_region,
                                                              context=context),
                                  from_test=False)
    if all_disjoint:
        return Relation.DISJOINT
    relation = process_compound_queue(events_queue,
                                      min(goal_regions_max_x,
                                          region_bounding_box.max_x))
    return (relation
            if none_disjoint
            else (Relation.COMPONENT
                  if relation is Relation.EQUAL
                  else (Relation.OVERLAP
                        if relation in (Relation.COVER,
                                        Relation.ENCLOSES,
                                        Relation.COMPOSITE)
                        else relation)))


def relate_multiregion(goal: Multiregion, test: Multiregion,
                       *,
                       context: Context) -> Relation:
    return (_relate_multiregion(goal, test,
                                box.from_contours(goal,
                                                  context=context),
                                box.from_contours(test,
                                                  context=context),
                                context=context)
            if goal and test
            else Relation.DISJOINT)


def _relate_multiregion(goal: Iterable[Region],
                        test: Iterable[Region],
                        goal_bounding_box: Box,
                        test_bounding_box: Box,
                        *,
                        context: Context) -> Relation:
    if box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_edges_endpoints(goal,
                                                      context=context),
                          from_test=False)
    events_queue.register(to_oriented_edges_endpoints(test,
                                                      context=context),
                          from_test=True)
    return process_compound_queue(events_queue, min(goal_bounding_box.max_x,
                                                    test_bounding_box.max_x))


def to_oriented_edges_endpoints(regions: Iterable[Region],
                                *,
                                clockwise: bool = False,
                                context: Context
                                ) -> Iterable[SegmentEndpoints]:
    for region in regions:
        yield from region_to_oriented_segments(region,
                                               clockwise=clockwise,
                                               context=context)
