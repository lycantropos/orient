from ground.hints import (Box,
                          Point)


def contains_point(box: Box, point: Point) -> bool:
    return (box.min_x <= point.x <= box.max_x
            and box.min_y <= point.y <= box.max_y)


def disjoint_with(goal: Box, test: Box) -> bool:
    return (goal.max_x < test.min_x or test.max_x < goal.min_x
            or goal.max_y < test.min_y or test.max_y < goal.min_y)
