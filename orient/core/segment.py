from robust.linear import segments_intersections

from orient.hints import Segment


def intersects_only_at_endpoints(left: Segment, right: Segment) -> bool:
    return all(point in left
               for point in segments_intersections(left, right))
