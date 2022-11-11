import enum
from typing import Optional


class GameResult(str, enum.Enum):
    UNKNOWN = "unknown"
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW = "draw"


class Game:
    def __init__(
        self,
        game_id: str,
        round_number: int,
        black_id: str,
        white_id: str,
        *,
        handicap: int = 0,
        result: GameResult = GameResult.UNKNOWN,
    ):
        self.game_id = game_id
        self.round_number = round_number
        self.black_id = black_id
        self.white_id = white_id

        self.handicap = handicap
        self.result = result

    def __repr__(self):
        return f"Game({self.game_id=}, {self.round_number=}, {self.black_id=}, {self.white_id=})"

    def __str__(self):
        return repr(self)

    def __eq__(self, other: "Game"):
        return self.game_id == other.game_id

    def __hash__(self):
        return hash(self.game_id)


class GameSet(set[Game]):
    def get(self, game_id: str) -> Optional[Game]:
        for game in self:
            if game.game_id == game_id:
                return game

    def get_player_games(self, player_id: str) -> "GameSet":
        return GameSet(
            game
            for game in self
            if game.black_id == player_id or game.white_id == player_id
        )

    def get_round_games(self, round_number: int) -> "GameSet":
        games = {game for game in self if game.round_number == round_number}
        return GameSet(games)

    def color_balance(self, player_id: str) -> int:
        as_white = len(
            {game for game in self if game.white_id == player_id and not game.handicap}
        )
        as_black = len(
            {game for game in self if game.black_id == player_id and not game.handicap}
        )
        return as_white - as_black
