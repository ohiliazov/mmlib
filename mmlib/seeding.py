from mmlib.constants import SeedingMode


def _validate_seeding_arguments(
    p1_idx: int,
    p2_idx: int,
    group_size: int,
) -> None:
    if group_size < 2:
        raise ValueError("`group_size` must be a greater or equal to 2.")

    if p1_idx > p2_idx:
        raise ValueError("`p1_idx` must be less than `p2_idx`.")

    if not 0 <= p1_idx < group_size:
        raise ValueError(f"`p1_idx` must be between 0 and {group_size-1}.")

    if not 0 <= p2_idx < group_size:
        raise ValueError(f"`p2_idx` must be between 0 and {group_size-1}.")


def seeding_cross(p1_idx: int, p2_idx: int, size: int) -> float:
    _validate_seeding_arguments(p1_idx, p2_idx, size)
    size += size % 2
    if size == 2:
        return 1
    return 1 - abs(2 * abs(p1_idx - p2_idx) - size) / (size - 2)


def seeding_fold(p1_idx: int, p2_idx: int, size: int) -> float:
    _validate_seeding_arguments(p1_idx, p2_idx, size)
    size += size % 2
    if size == 2:
        return 1

    return 1 - abs(p2_idx + p1_idx - size + 1) / (size - 2)


def seeding_adjacent(p1_idx: int, p2_idx: int, size: int) -> float:
    _validate_seeding_arguments(p1_idx, p2_idx, size)
    size += size % 2
    if size == 2:
        return 1
    return 1 - (abs(p1_idx - p2_idx) - 1) / (size - 2)


def seeding_coefficient(
    p1_idx: int,
    p2_idx: int,
    size: int,
    mode: SeedingMode,
) -> float:
    match mode:
        case SeedingMode.CROSS if size > 3:
            return seeding_cross(p1_idx, p2_idx, size)
        case SeedingMode.FOLD if size > 2:
            return seeding_fold(p1_idx, p2_idx, size)
        case SeedingMode.ADJACENT if size > 2:
            return seeding_adjacent(p1_idx, p2_idx, size)
        case _:
            raise ValueError(f"Unknown seeding mode: {mode}")
