import pytest
from mmlib.handicap import calculate_handicap
from mmlib.parameters import HandicapParameters


@pytest.mark.parametrize(
    "lower_rank, higher_rank, handicap_bar, handicap_correction, handicap_max, expected",
    [
        (-3, 2, 0, 0, 0, 0),  # 3k vs 3d - even
        (-3, 2, -30, 0, 9, 5),  # 3k vs 3d - 5 stones
        (-3, 2, -2, 0, 9, 4),  # 3k vs 3d (2k handicap bar) - 4 stones
        (-3, 2, -30, -1, 9, 4),  # 3k vs 3d (1 stone reduction) - 4 stones
        (-3, 2, -30, 0, 4, 4),  # 3k vs 3d (1 stone reduction) - 4 stones
    ],
)
def test_handicap(
    lower_rank: int,
    higher_rank: int,
    handicap_bar: int,
    handicap_correction: int,
    handicap_max: int,
    expected: int,
):
    handicap = calculate_handicap(
        lower_rank=lower_rank,
        higher_rank=higher_rank,
        handicap_params=HandicapParameters(
            handicap_bar=handicap_bar,
            handicap_correction=handicap_correction,
            handicap_max=handicap_max,
        ),
    )
    assert handicap == expected
