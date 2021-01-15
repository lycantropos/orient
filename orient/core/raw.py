from ground.hints import Contour, Multipolygon, Multisegment, Polygon


def from_multisegment(multisegment: Multisegment):
    return multisegment


def from_contour(contour: Contour):
    return contour.vertices


from_region = from_contour


def from_multiregion(multiregion):
    return [from_region(region) for region in multiregion]


def from_polygon(polygon: Polygon):
    return from_contour(polygon.border), from_multiregion(polygon.holes)


def from_multipolygon(multipolygon: Multipolygon):
    return [from_polygon(polygon) for polygon in multipolygon.polygons]
