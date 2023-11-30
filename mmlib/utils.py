from mmlib.constants import DUDDMode, SeedingMode


def calculate_handicap(
    r1: int,
    r2: int,
    hd_bar: int,
    hd_adj: int,
    hd_max: int,
) -> int:
    assert r1 <= r2, "r1 should not be higher than r2"

    return min(max(max(r2, hd_bar) - max(r1, hd_bar) + hd_adj, 0), hd_max)


def dudd_coefficient(place: int, group_size: int, mode: DUDDMode) -> float:
    if group_size == 0:
        return 1

    match mode:
        case DUDDMode.BOTTOM:
            return place / group_size

        case DUDDMode.TOP:
            return 1 - place / group_size

        case DUDDMode.MIDDLE:
            mid = group_size // 2
            place = group_size - place if place > mid else place
            return place / mid

    return 0


def seeding_coefficient(
    p1_idx: int, p2_idx: int, size: int, mode: SeedingMode
) -> float:
    match mode:
        case SeedingMode.CROSS if size > 3:
            term = abs(2 * abs(p1_idx - p2_idx) - size)
        case SeedingMode.FOLD if size > 2:
            term = abs(p2_idx + p1_idx - size + 1)
        case SeedingMode.ADJACENT if size > 2:
            term = abs(p1_idx - p2_idx) - 1
        case _:
            return 1

    return 1 - term / (size - 2)
