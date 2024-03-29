from typing import Iterable

from ground.base import (Context,
                         Location, Relation)
from ground.hints import (Contour,
                          Multisegment,
                          Point,
                          Polygon,
                          Segment)

from . import box
from .events_queue import CompoundEventsQueue
from .hints import (Multiregion,
                    Region,
                    SegmentEndpoints)
from .multiregion import (_relate_contour as relate_contour_to_multiregion,
                          _relate_region as relate_region_to_regions,
                          relate_multiregion as relate_multiregions,
                          relate_segment as relate_segment_to_multiregion,
                          to_oriented_edges_endpoints
                          as multiregion_to_oriented_segments)
from .multisegment import to_segments_endpoints
from .processing import process_linear_compound_queue
from .region import (_relate_contour as relate_contour_to_region,
                     _relate_region as relate_regions,
                     locate_point as locate_point_in_region,
                     relate_segment as relate_segment_to_region,
                     to_oriented_segments as region_to_oriented_segments)


def locate_point(polygon: Polygon,
                 point: Point,
                 context: Context) -> Location:
    location_without_holes = locate_point_in_region(polygon.border, point,
                                                    context)
    if location_without_holes is Location.INTERIOR:
        for hole in polygon.holes:
            location_in_hole = locate_point_in_region(hole, point, context)
            if location_in_hole is Location.INTERIOR:
                return Location.EXTERIOR
            elif location_in_hole is Location.BOUNDARY:
                return Location.BOUNDARY
    return location_without_holes


def relate_segment(polygon: Polygon,
                   segment: Segment,
                   context: Context) -> Relation:
    relation_without_holes = relate_segment_to_region(polygon.border, segment,
                                                      context)
    if (polygon.holes and (relation_without_holes is Relation.WITHIN
                           or relation_without_holes is Relation.ENCLOSED)):
        relation_with_holes = relate_segment_to_multiregion(polygon.holes,
                                                            segment, context)
        if relation_with_holes is Relation.DISJOINT:
            return relation_without_holes
        elif relation_with_holes is Relation.TOUCH:
            return Relation.ENCLOSED
        elif relation_with_holes is Relation.ENCLOSED:
            return Relation.TOUCH
        elif relation_with_holes is Relation.WITHIN:
            return Relation.DISJOINT
        else:
            return relation_with_holes
    else:
        return relation_without_holes


def relate_multisegment(polygon: Polygon,
                        multisegment: Multisegment,
                        context: Context) -> Relation:
    polygon_bounding_box = context.polygon_box(polygon)
    multisegment_bounding_box = context.segments_box(multisegment.segments)
    if box.disjoint_with(polygon_bounding_box, multisegment_bounding_box):
        return Relation.DISJOINT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_edges_endpoints(polygon, context),
                          from_test=False)
    events_queue.register(to_segments_endpoints(multisegment),
                          from_test=True)
    return process_linear_compound_queue(events_queue,
                                         min(multisegment_bounding_box.max_x,
                                             polygon_bounding_box.max_x))


def relate_contour(polygon: Polygon,
                   contour: Contour,
                   context: Context) -> Relation:
    contour_bounding_box = context.contour_box(contour)
    relation_without_holes = relate_contour_to_region(polygon.border, contour,
                                                      contour_bounding_box,
                                                      context)
    holes = polygon.holes
    if holes and (relation_without_holes is Relation.ENCLOSED
                  or relation_without_holes is Relation.WITHIN):
        relation_with_holes = relate_contour_to_multiregion(
                holes, contour, contour_bounding_box, context
        )
        if relation_with_holes is Relation.DISJOINT:
            return relation_without_holes
        elif relation_with_holes is Relation.TOUCH:
            return Relation.ENCLOSED
        elif (relation_with_holes is Relation.CROSS
              or relation_with_holes is Relation.COMPONENT):
            return relation_with_holes
        elif relation_with_holes is Relation.ENCLOSED:
            return Relation.TOUCH
        else:
            # contour is within holes
            return Relation.DISJOINT
    else:
        return relation_without_holes


def relate_region(polygon: Polygon,
                  region: Region,
                  context: Context) -> Relation:
    region_bounding_box = context.contour_box(region)
    border, holes = polygon.border, polygon.holes
    relation_with_border = relate_regions(border, region,
                                          context.contour_box(border),
                                          region_bounding_box, context)
    if relation_with_border in (Relation.DISJOINT,
                                Relation.TOUCH,
                                Relation.OVERLAP,
                                Relation.COVER,
                                Relation.ENCLOSES):
        return relation_with_border
    elif (relation_with_border is Relation.COMPOSITE
          or relation_with_border is Relation.EQUAL):
        return (Relation.ENCLOSES
                if holes
                else relation_with_border)
    else:
        relation_with_holes = relate_region_to_regions(holes, region,
                                                       region_bounding_box,
                                                       context)
        if relation_with_holes is Relation.DISJOINT:
            return relation_with_border
        elif relation_with_holes is Relation.TOUCH:
            return Relation.ENCLOSED
        elif relation_with_holes in (Relation.EQUAL,
                                     Relation.COMPONENT,
                                     Relation.ENCLOSED):
            return Relation.TOUCH
        elif relation_with_holes is Relation.WITHIN:
            return Relation.DISJOINT
        else:
            return Relation.OVERLAP


def relate_multiregion(polygon: Polygon,
                       multiregion: Multiregion,
                       context: Context) -> Relation:
    border, holes = polygon.border, polygon.holes
    border_bounding_box = context.contour_box(border)
    if not holes:
        return relate_region_to_regions(multiregion, border,
                                        border_bounding_box,
                                        context).complement
    none_touch = True
    subsets_regions_indices = []
    for region_index, region in enumerate(multiregion):
        region_relation = relate_regions(border, region, border_bounding_box,
                                         context.contour_box(region), context)
        if region_relation is Relation.TOUCH:
            if none_touch:
                none_touch = False
        elif region_relation in (Relation.OVERLAP,
                                 Relation.COVER,
                                 Relation.ENCLOSES):
            return region_relation
        elif (region_relation is Relation.COMPOSITE
              or region_relation is Relation.EQUAL):
            return Relation.ENCLOSES
        elif region_relation is not Relation.DISJOINT:
            if none_touch and (region_relation is Relation.ENCLOSED
                               or region_relation is Relation.COMPONENT):
                none_touch = False
            subsets_regions_indices.append(region_index)
    if subsets_regions_indices:
        is_subset_of_border = len(subsets_regions_indices) == len(multiregion)
        relation_with_holes = relate_multiregions(
                holes,
                multiregion
                if is_subset_of_border
                else [multiregion[index] for index in subsets_regions_indices],
                context
        )
        if relation_with_holes is Relation.DISJOINT:
            return ((Relation.WITHIN
                     if none_touch
                     else Relation.ENCLOSED)
                    if is_subset_of_border
                    else Relation.OVERLAP)
        elif relation_with_holes is Relation.TOUCH:
            return (Relation.ENCLOSED
                    if is_subset_of_border
                    else Relation.OVERLAP)
        elif relation_with_holes is Relation.OVERLAP:
            return relation_with_holes
        elif relation_with_holes in (Relation.COVER,
                                     Relation.ENCLOSES,
                                     Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_holes is Relation.WITHIN:
            return (Relation.DISJOINT
                    if none_touch
                    else Relation.TOUCH)
        else:
            return Relation.TOUCH
    else:
        return (Relation.DISJOINT
                if none_touch
                else Relation.TOUCH)


def relate_polygon(goal: Polygon,
                   test: Polygon,
                   context: Context) -> Relation:
    goal_bounding_box, test_bounding_box = (context.polygon_box(goal),
                                            context.polygon_box(test))
    goal_border, goal_holes = goal.border, goal.holes
    test_border, test_holes = test.border, test.holes
    borders_relation = relate_regions(goal_border, test_border,
                                      goal_bounding_box, test_bounding_box,
                                      context)
    if borders_relation in (Relation.DISJOINT,
                            Relation.TOUCH,
                            Relation.OVERLAP):
        return borders_relation
    elif borders_relation is Relation.EQUAL:
        if goal_holes and test_holes:
            holes_relation = relate_multiregions(test_holes, goal_holes,
                                                 context)
            if holes_relation in (Relation.DISJOINT,
                                  Relation.TOUCH,
                                  Relation.OVERLAP):
                return Relation.OVERLAP
            elif holes_relation in (Relation.COVER,
                                    Relation.ENCLOSES,
                                    Relation.COMPOSITE):
                return Relation.ENCLOSES
            elif holes_relation is Relation.EQUAL:
                return borders_relation
            else:
                return Relation.ENCLOSED
        else:
            return (Relation.ENCLOSES
                    if goal_holes
                    else (Relation.ENCLOSED
                          if test_holes
                          else Relation.EQUAL))
    elif borders_relation in (Relation.WITHIN,
                              Relation.ENCLOSED,
                              Relation.COMPONENT):
        if goal_holes:
            none_touch = True
            subsets_holes_indices = []
            for hole_index, hole in enumerate(goal_holes):
                hole_relation = relate_regions(test_border, hole,
                                               test_bounding_box,
                                               context.contour_box(hole),
                                               context)
                if hole_relation is Relation.TOUCH:
                    if none_touch:
                        none_touch = False
                elif hole_relation is Relation.OVERLAP:
                    return hole_relation
                elif hole_relation is Relation.COVER:
                    return Relation.DISJOINT
                elif hole_relation in (Relation.ENCLOSES,
                                       Relation.COMPOSITE,
                                       Relation.EQUAL):
                    return Relation.TOUCH
                elif hole_relation is not Relation.DISJOINT:
                    subsets_holes_indices.append(hole_index)
            if subsets_holes_indices:
                holes_relation = (
                    relate_multiregions(
                            test_holes,
                            goal_holes
                            if len(subsets_holes_indices) == len(goal_holes)
                            else [goal_holes[index]
                                  for index in subsets_holes_indices],
                            context
                    )
                    if test_holes
                    else Relation.DISJOINT
                )
                if holes_relation is Relation.EQUAL:
                    return (Relation.ENCLOSED
                            if borders_relation is Relation.WITHIN
                            else borders_relation)
                elif (holes_relation is Relation.COMPONENT
                      or holes_relation is Relation.ENCLOSED):
                    return Relation.ENCLOSED
                elif holes_relation is Relation.WITHIN:
                    return borders_relation
                else:
                    return Relation.OVERLAP
            else:
                return (borders_relation
                        if none_touch
                        else Relation.ENCLOSED)
        else:
            return (Relation.ENCLOSED
                    if test_holes and borders_relation is Relation.COMPONENT
                    else borders_relation)
    elif test_holes:
        none_touch = True
        subsets_holes_indices = []
        for hole_index, hole in enumerate(test_holes):
            hole_relation = relate_regions(goal_border, hole,
                                           goal_bounding_box,
                                           context.contour_box(hole), context)
            if hole_relation is Relation.TOUCH:
                if none_touch:
                    none_touch = False
            elif hole_relation is Relation.OVERLAP:
                return hole_relation
            elif hole_relation is Relation.COVER:
                return Relation.DISJOINT
            elif hole_relation in (Relation.ENCLOSES,
                                   Relation.COMPOSITE,
                                   Relation.EQUAL):
                return Relation.TOUCH
            elif hole_relation is not Relation.DISJOINT:
                subsets_holes_indices.append(hole_index)
        if subsets_holes_indices:
            holes_relation = (
                relate_multiregions(
                        goal_holes,
                        test_holes
                        if len(subsets_holes_indices) == len(test_holes)
                        else [test_holes[index]
                              for index in subsets_holes_indices],
                        context
                )
                if goal_holes
                else Relation.DISJOINT
            )
            if holes_relation is Relation.EQUAL:
                return (Relation.ENCLOSES
                        if borders_relation is Relation.COVER
                        else borders_relation)
            elif (holes_relation is Relation.COMPONENT
                  or holes_relation is Relation.ENCLOSED):
                return Relation.ENCLOSES
            elif holes_relation is Relation.WITHIN:
                return borders_relation
            else:
                return Relation.OVERLAP
        else:
            return (borders_relation
                    if none_touch
                    else Relation.ENCLOSES)
    else:
        return (Relation.ENCLOSES
                if goal_holes and borders_relation is Relation.COMPOSITE
                else borders_relation)


def to_oriented_edges_endpoints(polygon: Polygon,
                                context: Context,
                                clockwise: bool = False
                                ) -> Iterable[SegmentEndpoints]:
    yield from region_to_oriented_segments(polygon.border, context, clockwise)
    yield from multiregion_to_oriented_segments(polygon.holes, context,
                                                not clockwise)
