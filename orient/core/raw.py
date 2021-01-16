from ground.hints import Multipolygon, Polygon


def from_polygon(polygon: Polygon):
    return polygon.border, polygon.holes


def from_multipolygon(multipolygon: Multipolygon):
    return [from_polygon(polygon) for polygon in multipolygon.polygons]
