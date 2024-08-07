from mmlib.constants import SeedingMode


def cross_seeding(p1_idx: int, p2_idx: int, size: int) -> float:
    return 1 - abs(2 * abs(p1_idx - p2_idx) - size) / (size - 2)


def fold_seeding(p1_idx: int, p2_idx: int, size: int) -> float:
    return 1 - abs(p2_idx + p1_idx - size + 1) / (size - 2)


def adjacent_seeding(p1_idx: int, p2_idx: int, size: int) -> float:
    return 1 - (abs(p1_idx - p2_idx) - 1) / (size - 2)


def seeding_coefficient(
    p1_idx: int,
    p2_idx: int,
    size: int,
    mode: SeedingMode,
) -> float:
    match mode:
        case SeedingMode.CROSS if size > 3:
            return cross_seeding(p1_idx, p2_idx, size)
        case SeedingMode.FOLD if size > 2:
            return fold_seeding(p1_idx, p2_idx, size)
        case SeedingMode.ADJACENT if size > 2:
            return adjacent_seeding(p1_idx, p2_idx, size)
        case _:
            return 0
