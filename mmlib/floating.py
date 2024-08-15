from mmlib.constants import FloatingMode


def _validate_floating_arguments(place: int, group_size: int) -> None:
    if group_size < 1:
        raise ValueError("Group size must be a positive integer.")

    if place < 0:
        raise ValueError("Place must be a non-negative integer.")

    if place >= group_size:
        raise ValueError("Place must be less than group size.")


def floating_bottom(place: int, group_size: int) -> float:
    _validate_floating_arguments(place, group_size)

    if group_size < 2:
        return 1

    return place / (group_size - 1)


def floating_top(place: int, group_size: int) -> float:
    _validate_floating_arguments(place, group_size)

    if group_size < 2:
        return 1

    return 1 - place / (group_size - 1)


def floating_middle(place: int, group_size: int) -> float:
    _validate_floating_arguments(place, group_size)

    if group_size <= 2:
        return 1

    mid = (group_size - 1) // 2
    result = mid - abs(mid - place)
    if place > mid:
        result += 1 - group_size % 2
    return result / mid


def floating_coefficient(
    mode: FloatingMode,
    place: int,
    group_size: int,
) -> float:
    match mode:
        case FloatingMode.BOTTOM:
            return floating_bottom(place, group_size)
        case FloatingMode.TOP:
            return floating_top(place, group_size)
        case FloatingMode.MIDDLE:
            return floating_middle(place, group_size)
        case _:
            raise ValueError(f"Unknown floating mode: {mode}")
