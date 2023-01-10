from .parameters import HandicapParameters


def calculate_handicap(
    lower_rank: int,
    higher_rank: int,
    handicap_params: HandicapParameters,
) -> int:
    if lower_rank > higher_rank:
        raise Exception("lower_rank should be lower or equal to higher_rank!")

    lower_rank = max(lower_rank, handicap_params.handicap_bar)
    higher_rank = max(higher_rank, handicap_params.handicap_bar)
    handicap = higher_rank - lower_rank + handicap_params.handicap_correction

    return min(max(0, handicap), handicap_params.handicap_max)
