from typing import Tuple

from hypothesis import given

from orient.core.contour import edges
from orient.hints import (Contour,
                          Polygon)
from orient.planar import (Relation,
                           contour_in_polygon,
                           point_in_polygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication)
from . import strategies


@given(strategies.polygons_with_contours)
def test_basic(polygon_with_contour: Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_polygon(contour, (contour, [])) is Relation.COMPONENT


@given(strategies.polygons_with_contours)
def test_connection_with_point_in_polygon(polygon_with_contour
                                          : Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    vertices_relations = [point_in_polygon(vertex, polygon)
                          for vertex in contour]
    assert implication(result is Relation.DISJOINT,
                       all(vertex_relation is Relation.DISJOINT
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.TOUCH,
                       all(vertex_relation is not Relation.WITHIN
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.COMPONENT,
                       all(vertex_relation is Relation.COMPONENT
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.ENCLOSED,
                       all(vertex_relation is not Relation.DISJOINT
                           for vertex_relation in vertices_relations))
    assert implication(result is Relation.WITHIN,
                       all(vertex_relation is Relation.WITHIN
                           for vertex_relation in vertices_relations))
    assert implication(all(vertex_relation is Relation.DISJOINT
                           for vertex_relation in vertices_relations),
                       result is Relation.DISJOINT
                       or result is Relation.TOUCH
                       or result is Relation.CROSS)
    assert implication(all(vertex_relation is Relation.WITHIN
                           for vertex_relation in vertices_relations),
                       result is Relation.CROSS
                       or result is Relation.ENCLOSED
                       or result is Relation.WITHIN)
    assert implication(any(vertex_relation is Relation.DISJOINT
                           for vertex_relation in vertices_relations)
                       and any(vertex_relation is Relation.WITHIN
                               for vertex_relation in vertices_relations),
                       result is Relation.CROSS)


@given(strategies.polygons_with_contours)
def test_connection_with_segment_in_polygon(polygon_with_contour
                                            : Tuple[Polygon, Contour]) -> None:
    polygon, contour = polygon_with_contour

    result = contour_in_polygon(contour, polygon)

    edges_relations = [segment_in_polygon(edge, polygon)
                       for edge in edges(contour)]
    assert equivalence(result is Relation.DISJOINT,
                       all(edge_relation is Relation.DISJOINT
                           for edge_relation in edges_relations))
    assert equivalence(result is Relation.TOUCH,
                       all(edge_relation is not Relation.CROSS
                           and edge_relation is not Relation.ENCLOSED
                           and edge_relation is not Relation.WITHIN
                           for edge_relation in edges_relations)
                       and any(edge_relation is Relation.TOUCH
                               or edge_relation is Relation.COMPONENT
                               for edge_relation in edges_relations))
    assert equivalence(result is Relation.CROSS,
                       any(edge_relation is Relation.CROSS
                           for edge_relation in edges_relations)
                       or any(edge_relation is Relation.TOUCH
                              or edge_relation is Relation.DISJOINT
                              for edge_relation in edges_relations)
                       and any(edge_relation is Relation.ENCLOSED
                               or edge_relation is Relation.WITHIN
                               for edge_relation in edges_relations))
    assert equivalence(result is Relation.COMPONENT,
                       all(edge_relation is Relation.COMPONENT
                           for edge_relation in edges_relations))
    assert equivalence(result is Relation.ENCLOSED,
                       all(edge_relation is Relation.COMPONENT
                           or edge_relation is Relation.ENCLOSED
                           or edge_relation is Relation.WITHIN
                           for edge_relation in edges_relations)
                       and any(edge_relation is Relation.COMPONENT
                               or edge_relation is Relation.ENCLOSED
                               for edge_relation in edges_relations))
    assert equivalence(result is Relation.WITHIN,
                       all(edge_relation is Relation.WITHIN
                           for edge_relation in edges_relations))
