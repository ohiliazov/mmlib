from enum import IntEnum, StrEnum


class Weight(IntEnum):
    unique_game_weight = 500_000_000_000_000
    score_weight = 100_000_000_000
    dudd_weight = 100_000_000
    seeding_weight = 5_000_000
    color_weight = 1_000_000


class GameResult(StrEnum):
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW = "draw"


class FloatingMode(StrEnum):
    """
    If set to TOP the first player will be prioritised to be drawn up/down.
    If set to MIDDLE the middle player will be prioritised to drawn up/down.
    If set to BOTTOM the last player will be prioritised to drawn up/down.
    """

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class SeedingMode(StrEnum):
    """
    If set to CROSS the first player will be seeded with middle.
    If set to FOLD the first player will be seeded with last.
    If set to ADJACENT the first player will be seeded with second, third with fourth etc.
    """

    CROSS = "cross"
    FOLD = "fold"
    ADJACENT = "adjacent"
