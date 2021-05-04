from ground.hints import Box


def disjoint_with(goal: Box, test: Box) -> bool:
    return (goal.max_x < test.min_x or test.max_x < goal.min_x
            or goal.max_y < test.min_y or test.max_y < goal.min_y)
