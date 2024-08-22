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
    rank: int
    smms_x2: int


class Game(BaseModel):
    black_id: str
    white_id: str
    handicap: int
    result: GameResult | None = None

    def has_played(self, player_id: str) -> bool:
        return player_id == self.black_id or player_id == self.white_id

    def points_x2(self, player_id: str) -> int:
        if not self.has_played(player_id):
            return 0

        match self.result:
            case GameResult.WHITE_WINS if self.white_id == player_id:
                return 2
            case GameResult.BLACK_WINS if self.black_id == player_id:
                return 2
            case GameResult.DRAW:
                return 1
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
    points_x2: int = 0
    skipped_x2: int = 0
    mms_x2: int = 0
    score_x2: int = 0
    sos_x2: int = 0
    sosos_x2: int = 0
    draw_ups: int = 0
    draw_downs: int = 0
    color_balance: int = 0
    opponent_ids: set = Field(default_factory=set)

    @classmethod
    def from_player(cls, player: Player) -> "ScoredPlayer":
        return cls(
            player_id=player.player_id,
            rank=player.rank,
            smms_x2=player.smms_x2,
            mms_x2=player.smms_x2,
            score_x2=player.smms_x2,
        )

    @staticmethod
    def _rounded_x2(value: int) -> int:
        return value - value % 2

    def get_mms_x2(self):
        return self._rounded_x2(self.smms_x2 + self.points_x2)

    def get_score_x2(self):
        return self._rounded_x2(
            self.smms_x2 + self.points_x2 + self.skipped_x2
        )

    def placement_criteria(self):
        return -self.mms_x2, -self.sos_x2, -self.sosos_x2


class Tournament(BaseModel):
    players: list[Player]
    games: list[list[Game]]
    parameters: Parameters
