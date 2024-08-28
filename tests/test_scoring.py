from faker import Faker

from mmlib.constants import GameResult
from mmlib.models import Game, Player
from mmlib.scoring import make_scored_players

fake = Faker()


PLAYERS = [
    Player(player_id="p1", rank=2, smms=8),
    Player(player_id="p2", rank=2, smms=8),
    Player(player_id="p3", rank=0, smms=6),
    Player(player_id="p4", rank=0, smms=6),
    Player(player_id="p5", rank=-1, smms=5),
    Player(player_id="p6", rank=-2, smms=4),
    Player(player_id="p7", rank=-4, smms=2),
    Player(player_id="p8", rank=-6, smms=0),
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

    assert scored_players["p1"].smms == 8
    assert scored_players["p1"].points == 0
    assert scored_players["p1"].mms == 8
    assert scored_players["p1"].score == 8
    assert scored_players["p1"].color_balance == -1
    assert scored_players["p1"].draw_ups == 0

    assert scored_players["p2"].smms == 8
    assert scored_players["p2"].points == 1
    assert scored_players["p2"].mms == 9
    assert scored_players["p2"].score == 9
    assert scored_players["p2"].color_balance == 1
    assert scored_players["p2"].draw_ups == 0

    assert scored_players["p3"].smms == 6
    assert scored_players["p3"].points == 1
    assert scored_players["p3"].mms == 7
    assert scored_players["p3"].score == 7
    assert scored_players["p3"].color_balance == -1
    assert scored_players["p3"].draw_ups == 0

    assert scored_players["p4"].smms == 6
    assert scored_players["p4"].points == 0
    assert scored_players["p4"].mms == 6
    assert scored_players["p4"].score == 6
    assert scored_players["p4"].color_balance == 1
    assert scored_players["p4"].draw_ups == 0

    assert scored_players["p5"].smms == 5
    assert scored_players["p5"].points == 1
    assert scored_players["p5"].mms == 6
    assert scored_players["p5"].score == 6
    assert scored_players["p5"].color_balance == -1
    assert scored_players["p5"].draw_ups == 0
    assert scored_players["p5"].draw_downs == 1

    assert scored_players["p6"].smms == 4
    assert scored_players["p6"].points == 0
    assert scored_players["p6"].mms == 4
    assert scored_players["p6"].score == 4
    assert scored_players["p6"].color_balance == 1
    assert scored_players["p6"].draw_ups == 1
    assert scored_players["p6"].draw_downs == 0

    assert scored_players["p7"].smms == 2
    assert scored_players["p7"].points == 0
    assert scored_players["p7"].mms == 2
    assert scored_players["p7"].score == 2
    assert scored_players["p7"].color_balance == -1
    assert scored_players["p7"].draw_ups == 0
    assert scored_players["p7"].draw_downs == 1

    assert scored_players["p8"].smms == 0
    assert scored_players["p8"].points == 1
    assert scored_players["p8"].mms == 1
    assert scored_players["p8"].score == 1
    assert scored_players["p8"].color_balance == 1
    assert scored_players["p8"].draw_ups == 1
    assert scored_players["p8"].draw_downs == 0
