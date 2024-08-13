import pytest

from mmlib.constants import FloatingMode
from mmlib.floating import (
    floating_bottom,
    floating_coefficient,
    floating_middle,
    floating_top,
)


@pytest.mark.parametrize(
    "place,group_size,expected",
    [
        (0, 1, 1),
        (3, 4, 1),
        (2, 4, 0.667),
        (1, 4, 0.333),
        (0, 4, 0),
        (4, 5, 1),
        (3, 5, 0.75),
        (2, 5, 0.5),
        (1, 5, 0.25),
        (0, 5, 0),
        (5, 6, 1),
        (4, 6, 0.8),
        (3, 6, 0.6),
        (2, 6, 0.4),
        (1, 6, 0.2),
        (0, 6, 0),
    ],
)
def test_floating_bottom(place, group_size, expected):
    assert pytest.approx(floating_bottom(place, group_size), 0.01) == expected


@pytest.mark.parametrize(
    "place,group_size,expected",
    [
        (0, 1, 1),
        (0, 4, 1),
        (1, 4, 0.667),
        (2, 4, 0.333),
        (3, 4, 0),
        (0, 5, 1),
        (1, 5, 0.75),
        (2, 5, 0.5),
        (3, 5, 0.25),
        (4, 5, 0),
        (0, 6, 1),
        (1, 6, 0.8),
        (2, 6, 0.6),
        (3, 6, 0.4),
        (4, 6, 0.2),
        (5, 6, 0),
    ],
)
def test_floating_top(place, group_size, expected):
    assert pytest.approx(floating_top(place, group_size), 0.01) == expected


@pytest.mark.parametrize(
    "place,group_size,expected",
    [
        (0, 1, 1),
        (0, 4, 0),
        (1, 4, 1),
        (2, 4, 1),
        (3, 4, 0),
        (0, 5, 0),
        (1, 5, 0.5),
        (2, 5, 1),
        (3, 5, 0.5),
        (4, 5, 0),
        (0, 6, 0),
        (1, 6, 0.5),
        (2, 6, 1),
        (3, 6, 1),
        (4, 6, 0.5),
        (5, 6, 0),
    ],
)
def test_floating_middle(place, group_size, expected):
    assert pytest.approx(floating_middle(place, group_size), 0.01) == expected


@pytest.mark.parametrize(
    "mode,place,group_size,expected",
    [
        (FloatingMode.BOTTOM, 1, 6, 0.2),
        (FloatingMode.TOP, 1, 6, 0.8),
        (FloatingMode.MIDDLE, 1, 6, 0.5),
    ],
)
def test_floating_coefficients(mode, place, group_size, expected):
    assert (
        pytest.approx(floating_coefficient(mode, place, group_size), 0.01)
        == expected
    )
