from ground.hints import Contour, Multipolygon, Multisegment, Point, Polygon, \
    Segment


def from_point(point: Point):
    return point


def from_segment(segment: Segment):
    return from_point(segment.start), from_point(segment.end)


def from_multisegment(multisegment: Multisegment):
    return [from_segment(segment) for segment in multisegment.segments]


def from_contour(contour: Contour):
    return [from_point(vertex) for vertex in contour.vertices]


from_region = from_contour


def from_multiregion(multiregion):
    return [from_region(region) for region in multiregion]


def from_polygon(polygon: Polygon):
    return from_contour(polygon.border), from_multiregion(polygon.holes)


def from_multipolygon(multipolygon: Multipolygon):
    return [from_polygon(polygon) for polygon in multipolygon.polygons]
