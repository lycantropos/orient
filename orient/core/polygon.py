from orient.hints import (Point,
                          Polygon,
                          Segment)
from .contour import (relate_contour as relate_contours,
                      relate_point as relate_point_to_contour,
                      relate_segment as relate_segment_to_contour)
from .multicontour import (relate_contour as relate_contour_to_multicontour,
                           relate_multicontour as relate_multicontours)
from .relation import Relation


def relate_point(polygon: Polygon, point: Point) -> Relation:
    border, holes = polygon
    border_location = relate_point_to_contour(border, point)
    if border_location is Relation.WITHIN:
        for hole in holes:
            hole_relation = relate_point_to_contour(hole, point)
            if hole_relation is Relation.WITHIN:
                return Relation.DISJOINT
            elif hole_relation is Relation.COMPONENT:
                return Relation.COMPONENT
    return border_location


def relate_segment(polygon: Polygon, segment: Segment) -> Relation:
    border, holes = polygon
    border_relation = relate_segment_to_contour(border, segment)
    if (border_relation is Relation.WITHIN
            or border_relation is Relation.ENCLOSED):
        for hole in holes:
            hole_relation = relate_segment_to_contour(hole, segment)
            if hole_relation is Relation.WITHIN:
                return Relation.DISJOINT
            elif hole_relation is Relation.COMPONENT:
                return Relation.COMPONENT
            elif hole_relation is Relation.CROSS:
                return Relation.CROSS
            elif hole_relation is Relation.ENCLOSED:
                return Relation.TOUCH
            elif hole_relation is Relation.TOUCH:
                border_relation = Relation.ENCLOSED
    return border_relation


def relate_polygon(goal: Polygon, test: Polygon) -> Relation:
    goal_border, goal_holes = goal
    test_border, test_holes = test
    borders_relation = relate_contours(goal_border, test_border)
    if borders_relation in (Relation.DISJOINT, Relation.TOUCH,
                            Relation.OVERLAP):
        return borders_relation
    elif borders_relation is Relation.EQUAL:
        if goal_holes and test_holes:
            relation_with_holes = relate_multicontours(test_holes, goal_holes)
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
            relation_with_border = relate_contour_to_multicontour(goal_holes,
                                                                  test_border)
            if relation_with_border is Relation.DISJOINT:
                return borders_relation
            elif relation_with_border is Relation.WITHIN:
                return Relation.DISJOINT
            elif relation_with_border in (Relation.ENCLOSED,
                                          Relation.COMPONENT,
                                          Relation.EQUAL):
                return Relation.TOUCH
            elif relation_with_border in (Relation.OVERLAP,
                                          Relation.COMPOSITE):
                return Relation.OVERLAP
            elif relation_with_border is Relation.TOUCH:
                return Relation.ENCLOSED
            elif test_holes:
                relation_with_holes = relate_multicontours(test_holes,
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
            relation_with_border = relate_contour_to_multicontour(test_holes,
                                                                  goal_border)
            if relation_with_border is Relation.DISJOINT:
                return borders_relation
            elif relation_with_border is Relation.WITHIN:
                return Relation.DISJOINT
            elif relation_with_border in (Relation.ENCLOSED,
                                          Relation.COMPONENT,
                                          Relation.EQUAL):
                return Relation.TOUCH
            elif relation_with_border in (Relation.OVERLAP,
                                          Relation.COMPOSITE):
                return Relation.OVERLAP
            elif relation_with_border is Relation.TOUCH:
                return Relation.ENCLOSES
            elif goal_holes:
                relation_with_holes = relate_multicontours(goal_holes,
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
