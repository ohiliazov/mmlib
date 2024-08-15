import pytest

from mmlib.seeding import seeding_adjacent, seeding_cross, seeding_fold


@pytest.mark.parametrize(
    "p1_idx,p2_idx,group_size,expected",
    [
        (0, 1, 2, 1),
        (0, 1, 5, 0),
        (0, 2, 5, 0.25),
        (0, 3, 5, 0.5),
        (0, 4, 5, 0.75),
        (1, 2, 5, 0.5),
        (1, 3, 5, 0.75),
        (1, 4, 5, 1),
        (2, 3, 5, 1),
        (2, 4, 5, 0.75),
        (3, 4, 5, 0.5),
        (0, 1, 6, 0),
        (0, 2, 6, 0.25),
        (0, 3, 6, 0.5),
        (0, 4, 6, 0.75),
        (0, 5, 6, 1),
        (1, 2, 6, 0.5),
        (1, 3, 6, 0.75),
        (1, 4, 6, 1),
        (1, 5, 6, 0.75),
        (2, 3, 6, 1),
        (2, 4, 6, 0.75),
        (2, 5, 6, 0.5),
        (3, 4, 6, 0.5),
        (3, 5, 6, 0.25),
        (4, 5, 6, 0),
    ],
)
def test_seeding_fold(p1_idx, p2_idx, group_size, expected):
    assert (
        pytest.approx(seeding_fold(p1_idx, p2_idx, group_size), 0.01)
        == expected
    )


@pytest.mark.parametrize(
    "p1_idx,p2_idx,group_size,expected",
    [
        (0, 1, 2, 1),
        (0, 1, 6, 1),
        (0, 2, 6, 0.75),
        (0, 3, 6, 0.5),
        (0, 4, 6, 0.25),
        (0, 5, 6, 0),
        (1, 2, 6, 1),
        (1, 3, 6, 0.75),
        (1, 4, 6, 0.5),
        (1, 5, 6, 0.25),
        (2, 3, 6, 1),
        (2, 4, 6, 0.75),
        (2, 5, 6, 0.5),
        (3, 4, 6, 1),
        (3, 5, 6, 0.75),
        (4, 5, 6, 1),
        (0, 1, 5, 1),
        (0, 2, 5, 0.75),
        (0, 3, 5, 0.5),
        (0, 4, 5, 0.25),
        (1, 2, 5, 1),
        (1, 3, 5, 0.75),
        (1, 4, 5, 0.5),
        (2, 3, 5, 1),
        (2, 4, 5, 0.75),
        (3, 4, 5, 1),
    ],
)
def test_seeding_adjacent(p1_idx, p2_idx, group_size, expected):
    assert (
        pytest.approx(seeding_adjacent(p1_idx, p2_idx, group_size), 0.01)
        == expected
    )


@pytest.mark.parametrize(
    "p1_idx,p2_idx,group_size,expected",
    [
        (0, 1, 2, 1),
        (0, 1, 6, 0),
        (0, 2, 6, 0.5),
        (0, 3, 6, 1),
        (0, 4, 6, 0.5),
        (0, 5, 6, 0),
        (1, 2, 6, 0),
        (1, 3, 6, 0.5),
        (1, 4, 6, 1),
        (1, 5, 6, 0.5),
        (2, 3, 6, 0),
        (2, 4, 6, 0.5),
        (2, 5, 6, 1),
        (3, 4, 6, 0),
        (3, 5, 6, 0.5),
        (4, 5, 6, 0),
        (0, 1, 5, 0),
        (0, 2, 5, 0.5),
        (0, 3, 5, 1),
        (0, 4, 5, 0.5),
        (1, 2, 5, 0),
        (1, 3, 5, 0.5),
        (1, 4, 5, 1),
        (2, 3, 5, 0),
        (2, 4, 5, 0.5),
        (3, 4, 5, 0),
    ],
)
def test_seeding_cross(p1_idx, p2_idx, group_size, expected):
    assert (
        pytest.approx(seeding_cross(p1_idx, p2_idx, group_size), 0.01)
        == expected
    )
