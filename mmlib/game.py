import enum


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
