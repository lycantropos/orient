from orient.hints import (Contour,
                          Point,
                          Polygon,
                          Region,
                          Segment)
from .multiregion import (relate_multiregion as relate_multiregions,
                          relate_region as relate_region_to_multiregion)
from .region import (_to_contour_relation,
                     relate_point as relate_point_to_region,
                     relate_region as relate_regions,
                     relate_segment as relate_segment_to_region)
from .relation import Relation


def relate_point(polygon: Polygon, point: Point) -> Relation:
    border, holes = polygon
    relation_with_border = relate_point_to_region(border, point)
    if relation_with_border is Relation.WITHIN:
        for hole in holes:
            relation_with_hole = relate_point_to_region(hole, point)
            if relation_with_hole is Relation.WITHIN:
                return Relation.DISJOINT
            elif relation_with_hole is Relation.COMPONENT:
                return Relation.COMPONENT
    return relation_with_border


def relate_segment(polygon: Polygon, segment: Segment) -> Relation:
    border, holes = polygon
    relation_with_border = relate_segment_to_region(border, segment)
    if (relation_with_border is Relation.WITHIN
            or relation_with_border is Relation.ENCLOSED):
        for hole in holes:
            relation_with_hole = relate_segment_to_region(hole, segment)
            if relation_with_hole is Relation.WITHIN:
                return Relation.DISJOINT
            elif relation_with_hole is Relation.COMPONENT:
                return Relation.COMPONENT
            elif relation_with_hole is Relation.CROSS:
                return Relation.CROSS
            elif relation_with_hole is Relation.ENCLOSED:
                return Relation.TOUCH
            elif relation_with_hole is Relation.TOUCH:
                relation_with_border = Relation.ENCLOSED
    return relation_with_border


def relate_contour(goal: Polygon, test: Contour) -> Relation:
    return _to_contour_relation(relate_region(goal, test))


def relate_region(polygon: Polygon, region: Region) -> Relation:
    border, holes = polygon
    relation_with_border = relate_regions(border, region)
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
    elif holes:
        relation_with_holes = relate_region_to_multiregion(holes, region)
        if relation_with_holes is Relation.DISJOINT:
            return relation_with_border
        elif relation_with_holes is Relation.WITHIN:
            return Relation.DISJOINT
        elif relation_with_holes is Relation.TOUCH:
            return Relation.ENCLOSED
        elif (relation_with_holes is Relation.OVERLAP
              or relation_with_holes is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_holes in (Relation.ENCLOSED,
                                     Relation.COMPONENT,
                                     Relation.EQUAL):
            return Relation.TOUCH
        else:
            return Relation.OVERLAP
    else:
        return relation_with_border


def relate_polygon(goal: Polygon, test: Polygon) -> Relation:
    goal_border, goal_holes = goal
    test_border, test_holes = test
    borders_relation = relate_regions(goal_border, test_border)
    if borders_relation in (Relation.DISJOINT, Relation.TOUCH,
                            Relation.OVERLAP):
        return borders_relation
    elif borders_relation is Relation.EQUAL:
        if goal_holes and test_holes:
            relation_with_holes = relate_multiregions(test_holes, goal_holes)
            if relation_with_holes in (Relation.DISJOINT,
                                       Relation.TOUCH,
                                       Relation.OVERLAP):
                return Relation.OVERLAP
            elif relation_with_holes is Relation.COVER:
                return Relation.ENCLOSES
            elif relation_with_holes is Relation.WITHIN:
                return Relation.ENCLOSED
            else:
                return relation_with_holes
        else:
            return (Relation.ENCLOSES
                    if goal_holes
                    else (Relation.ENCLOSED
                          if test_holes
                          else Relation.EQUAL))
    elif borders_relation in (Relation.WITHIN, Relation.ENCLOSED,
                              Relation.COMPONENT):
        if goal_holes:
            relation_with_border = relate_region_to_multiregion(goal_holes,
                                                                test_border)
            if relation_with_border is Relation.DISJOINT:
                return borders_relation
            elif relation_with_border is Relation.WITHIN:
                return Relation.DISJOINT
            elif relation_with_border in (Relation.ENCLOSED,
                                          Relation.COMPONENT,
                                          Relation.EQUAL):
                return Relation.TOUCH
            elif (relation_with_border is Relation.OVERLAP
                  or relation_with_border is Relation.COMPOSITE):
                return Relation.OVERLAP
            elif relation_with_border is Relation.TOUCH:
                return Relation.ENCLOSED
            elif test_holes:
                relation_with_holes = relate_multiregions(test_holes,
                                                          goal_holes)
                return (borders_relation
                        if relation_with_holes in (Relation.EQUAL,
                                                   Relation.COMPONENT,
                                                   Relation.ENCLOSED,
                                                   Relation.WITHIN)
                        else Relation.OVERLAP)
            else:
                return Relation.OVERLAP
        else:
            return (Relation.ENCLOSED
                    if test_holes and borders_relation is Relation.COMPONENT
                    else borders_relation)
    else:
        if test_holes:
            relation_with_border = relate_region_to_multiregion(test_holes,
                                                                goal_border)
            if relation_with_border is Relation.DISJOINT:
                return borders_relation
            elif relation_with_border is Relation.WITHIN:
                return Relation.DISJOINT
            elif relation_with_border in (Relation.ENCLOSED,
                                          Relation.COMPONENT,
                                          Relation.EQUAL):
                return Relation.TOUCH
            elif (relation_with_border is Relation.OVERLAP
                  or relation_with_border is Relation.COMPOSITE):
                return Relation.OVERLAP
            elif relation_with_border is Relation.TOUCH:
                return Relation.ENCLOSES
            elif goal_holes:
                relation_with_holes = relate_multiregions(goal_holes,
                                                          test_holes)
                return (borders_relation
                        if relation_with_holes in (Relation.EQUAL,
                                                   Relation.COMPONENT,
                                                   Relation.ENCLOSED,
                                                   Relation.WITHIN)
                        else Relation.OVERLAP)
            else:
                return Relation.OVERLAP
        else:
            return (Relation.ENCLOSES
                    if goal_holes and borders_relation is Relation.COMPOSITE
                    else borders_relation)
