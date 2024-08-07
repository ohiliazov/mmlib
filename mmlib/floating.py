from mmlib.constants import FloatingMode


def floating_bottom(place: int, group_size: int) -> float:
    return place / group_size


def floating_top(place: int, group_size: int) -> float:
    return 1 - place / group_size


def floating_middle(place: int, group_size: int) -> float:
    mid = group_size // 2
    if place > mid:
        place = group_size - place
    return place / mid


def floating_coefficient(
    place: int,
    group_size: int,
    mode: FloatingMode,
) -> float:
    if group_size < 2:
        return 1

    match mode:
        case FloatingMode.BOTTOM:
            return floating_bottom(place, group_size)
        case FloatingMode.TOP:
            return floating_top(place, group_size)
        case FloatingMode.MIDDLE:
            return floating_middle(place, group_size)
        case _:
            raise ValueError(f"Unknown floating mode: {mode}")
