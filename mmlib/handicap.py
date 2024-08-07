def calculate_handicap(
    r1: int,
    r2: int,
    hd_bar: int,
    hd_adj: int,
    hd_max: int,
) -> int:
    assert r1 <= r2, "r1 should not be higher than r2"

    return min(max(max(r2, hd_bar) - max(r1, hd_bar) + hd_adj, 0), hd_max)
