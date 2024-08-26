from faker import Faker

from mmlib.constants import GameResult
from mmlib.models import Game, Player
from mmlib.scoring import make_scored_players

fake = Faker()


PLAYERS = [
    Player(player_id="p1", rank=2, smms_x2=16),
    Player(player_id="p2", rank=2, smms_x2=16),
    Player(player_id="p3", rank=0, smms_x2=12),
    Player(player_id="p4", rank=0, smms_x2=12),
    Player(player_id="p5", rank=-1, smms_x2=10),
    Player(player_id="p6", rank=-2, smms_x2=8),
    Player(player_id="p7", rank=-4, smms_x2=4),
    Player(player_id="p8", rank=-6, smms_x2=0),
]
GAMES_ROUND_1 = [
    Game(
        black_id="p1",
        white_id="p2",
        handicap=0,
        result=GameResult.WHITE_WINS,
    ),
    Game(
        black_id="p3",
        white_id="p4",
        handicap=0,
        result=GameResult.BLACK_WINS,
    ),
    Game(
        black_id="p5",
        white_id="p6",
        handicap=0,
        result=GameResult.BLACK_WINS,
    ),
    Game(
        black_id="p7",
        white_id="p8",
        handicap=0,
        result=GameResult.WHITE_WINS,
    ),
]


def test_scoring_round_1():
    scored_players = make_scored_players(PLAYERS, [GAMES_ROUND_1])

    assert scored_players["p1"].smms_x2 == 16
    assert scored_players["p1"].points_x2 == 0
    assert scored_players["p1"].score_x2 == 16
    assert scored_players["p1"].mms_x2 == 16
    assert scored_players["p1"].color_balance == -1
    assert scored_players["p1"].draw_ups == 0

    assert scored_players["p2"].smms_x2 == 16
    assert scored_players["p2"].points_x2 == 2
    assert scored_players["p2"].score_x2 == 18
    assert scored_players["p2"].mms_x2 == 18
    assert scored_players["p2"].color_balance == 1
    assert scored_players["p2"].draw_ups == 0

    assert scored_players["p3"].smms_x2 == 12
    assert scored_players["p3"].points_x2 == 2
    assert scored_players["p3"].score_x2 == 14
    assert scored_players["p3"].mms_x2 == 14
    assert scored_players["p3"].color_balance == -1
    assert scored_players["p3"].draw_ups == 0

    assert scored_players["p4"].smms_x2 == 12
    assert scored_players["p4"].points_x2 == 0
    assert scored_players["p4"].score_x2 == 12
    assert scored_players["p4"].mms_x2 == 12
    assert scored_players["p4"].color_balance == 1
    assert scored_players["p4"].draw_ups == 0

    assert scored_players["p5"].smms_x2 == 10
    assert scored_players["p5"].points_x2 == 2
    assert scored_players["p5"].score_x2 == 12
    assert scored_players["p5"].mms_x2 == 12
    assert scored_players["p5"].color_balance == -1
    assert scored_players["p5"].draw_ups == 0
    assert scored_players["p5"].draw_downs == 1

    assert scored_players["p6"].smms_x2 == 8
    assert scored_players["p6"].points_x2 == 0
    assert scored_players["p6"].score_x2 == 8
    assert scored_players["p6"].mms_x2 == 8
    assert scored_players["p6"].color_balance == 1
    assert scored_players["p6"].draw_ups == 1
    assert scored_players["p6"].draw_downs == 0

    assert scored_players["p7"].smms_x2 == 4
    assert scored_players["p7"].points_x2 == 0
    assert scored_players["p7"].score_x2 == 4
    assert scored_players["p7"].mms_x2 == 4
    assert scored_players["p7"].color_balance == -1
    assert scored_players["p7"].draw_ups == 0
    assert scored_players["p7"].draw_downs == 1

    assert scored_players["p8"].smms_x2 == 0
    assert scored_players["p8"].points_x2 == 2
    assert scored_players["p8"].score_x2 == 2
    assert scored_players["p8"].mms_x2 == 2
    assert scored_players["p8"].color_balance == 1
    assert scored_players["p8"].draw_ups == 1
    assert scored_players["p8"].draw_downs == 0
