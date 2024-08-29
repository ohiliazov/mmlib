from pydantic import BaseModel, Field

from mmlib.constants import FloatingMode, GameResult, SeedingMode


class Parameters(BaseModel):
    hd_bar: int = 0
    hd_adj: int = 0
    hd_max: int = 0
    dudd_compensate: bool = True
    float_up_mode: FloatingMode = FloatingMode.MIDDLE
    float_down_mode: FloatingMode = FloatingMode.MIDDLE
    seeding_mode: SeedingMode = SeedingMode.CROSS


class Player(BaseModel):
    player_id: str
    rank: int = 0
    smms: int = 0
    is_bye: bool = False


class Game(BaseModel):
    black_id: str
    white_id: str
    handicap: int = 0
    result: GameResult | None = None

    def has_played(self, player_id: str) -> bool:
        return player_id == self.black_id or player_id == self.white_id

    def points(self, player_id: str) -> float:
        if not self.has_played(player_id):
            return 0

        match self.result:
            case GameResult.WHITE_WINS if self.white_id == player_id:
                return 1
            case GameResult.BLACK_WINS if self.black_id == player_id:
                return 1
            case GameResult.DRAW:
                return 0.5
        return 0

    def opponent_id(self, player_id: str) -> str | None:
        if self.white_id == player_id:
            return self.black_id
        if self.black_id == player_id:
            return self.white_id

    def color_balance(self, player_id: str) -> int:
        if self.handicap == 0:
            if self.black_id == player_id:
                return -1
            if self.white_id == player_id:
                return 1
        return 0


class ScoredPlayer(Player):
    points: float = 0.0
    skips: int = 0
    draw_ups: int = 0
    draw_downs: int = 0
    color_balance: int = 0
    mms: int = 0
    score: int = 0
    sos: int = 0
    sosos: int = 0
    sodos: int = 0
    games: list[Game] = Field(default_factory=list)

    @classmethod
    def from_player(cls, player: Player) -> "ScoredPlayer":
        return cls(
            player_id=player.player_id,
            rank=player.rank,
            smms=player.smms,
            mms=player.smms,
            score=player.smms,
        )


class Tournament(BaseModel):
    players: list[Player]
    games: list[list[Game]]
    parameters: Parameters
