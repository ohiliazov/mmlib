import pytest
from faker import Faker

from mmlib.models import Player, ScoredPlayer
from mmlib.scoring import make_scored_players

fake = Faker()


@pytest.mark.parametrize(
    "players,games,scored_players",
    [
        ([], [], {}),
        (
            [Player(player_id="p1", rank=0, smms_x2=0)],
            [],
            {"p1": ScoredPlayer(player_id="p1", rank=0, smms_x2=0)},
        ),
        (
            [
                Player(player_id="p1", rank=0, smms_x2=0),
                Player(player_id="p2", rank=0, smms_x2=0),
            ],
            [],
            {
                "p1": ScoredPlayer(player_id="p1", rank=0, smms_x2=0),
                "p2": ScoredPlayer(player_id="p2", rank=0, smms_x2=0),
            },
        ),
        (
            [
                Player(player_id="p1", rank=3, smms_x2=6),
                Player(player_id="p2", rank=0, smms_x2=0),
            ],
            [],
            {
                "p1": ScoredPlayer(
                    player_id="p1",
                    rank=3,
                    smms_x2=6,
                    points_x2=0,
                    mms_x2=6,
                    score_x2=6,
                ),
                "p2": ScoredPlayer(player_id="p2", rank=0, smms_x2=0),
            },
        ),
    ],
)
def test_scored_players_without_games(players, games, scored_players):
    assert make_scored_players(players, games) == scored_players
