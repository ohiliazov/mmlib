import pytest
from faker import Faker

from mmlib.constants import GameResult
from mmlib.models import Game, Player
from mmlib.scoring import make_scored_players

fake = Faker()


@pytest.mark.parametrize(
    "players,games,points_x2_dict",
    [
        ([], [], {}),
        (
            [
                Player(player_id="p1", rank=0, smms_x2=0),
                Player(player_id="p2", rank=0, smms_x2=0),
            ],
            [],
            {"p1": 0, "p2": 0},
        ),
        (
            [
                Player(player_id="p1", rank=3, smms_x2=2),
                Player(player_id="p2", rank=-10, smms_x2=0),
            ],
            [],
            {"p1": 0, "p2": 0},
        ),
        (
            [
                Player(player_id="p1", rank=3, smms_x2=2),
                Player(player_id="p2", rank=-10, smms_x2=0),
            ],
            [
                [
                    Game(
                        black_id="p1",
                        white_id="p2",
                        handicap=0,
                        result=GameResult.BLACK_WINS,
                    )
                ]
            ],
            {"p1": 2, "p2": 0},
        ),
        (
            [
                Player(player_id="p1", rank=3, smms_x2=2),
                Player(player_id="p2", rank=-10, smms_x2=0),
            ],
            [
                [
                    Game(
                        black_id="p1",
                        white_id="p2",
                        handicap=0,
                        result=GameResult.WHITE_WINS,
                    )
                ]
            ],
            {"p1": 0, "p2": 2},
        ),
        (
            [
                Player(player_id="p1", rank=3, smms_x2=2),
                Player(player_id="p2", rank=-10, smms_x2=0),
            ],
            [
                [
                    Game(
                        black_id="p1",
                        white_id="p2",
                        handicap=0,
                        result=GameResult.DRAW,
                    )
                ]
            ],
            {"p1": 1, "p2": 1},
        ),
    ],
)
def test_points_x2(players, games, points_x2_dict):
    scores_dict = make_scored_players(players, games)
    for player_id, scored_player in scores_dict.items():
        assert scored_player.points_x2 == points_x2_dict[player_id]
