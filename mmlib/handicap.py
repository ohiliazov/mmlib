def calculate_handicap(
    p1_rank: int,
    p2_rank: int,
    handicap_bar: int,
    handicap_correction: int,
    handicap_max: int,
) -> int:
    if p1_rank > p2_rank:
        raise Exception("p1_rank should be lower or equal to p2_rank!")

    p1_rank = min(p1_rank, handicap_bar)
    p2_rank = min(p2_rank, handicap_bar)

    return min(max(0, p2_rank - p1_rank + handicap_correction), handicap_max)
