from pydantic import BaseModel

from mmlib.constants import DUDDMode, GameResult, SeedingMode


class Parameters(BaseModel):
    hd_bar: int = 0
    hd_adj: int = 0
    hd_max: int = 0
    dudd_compensate: bool = True
    du_mode: DUDDMode = DUDDMode.MIDDLE
    dd_mode: DUDDMode = DUDDMode.MIDDLE
    seeding_mode: SeedingMode = SeedingMode.CROSS


class Player(BaseModel):
    player_id: str
    rank: int
    smms_x2: int


class Game(BaseModel):
    black_id: str
    white_id: str
    handicap: int
    result: GameResult = GameResult.UNKNOWN
    use_color: bool = True

    def has_played(self, player_id: str) -> bool:
        return player_id == self.black_id or player_id == self.white_id

    def points_x2(self, player_id: str) -> int:
        if not self.has_played(player_id):
            return 0

        match self.result:
            case GameResult.BOTH_WIN:
                return 2
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
        if self.use_color and not self.handicap:
            if self.black_id == player_id:
                return -1
            if self.white_id == player_id:
                return 1
        return 0


class ScoredPlayer(Player):
    points_x2: int = 0
    skipped_x2: int = 0

    @property
    def mms_x2(self):
        return self.smms_x2 + self.points_x2

    @property
    def score_x2(self):
        return self.mms_x2 + self.skipped_x2

    sos_x2: int = 0
    sosos_x2: int = 0

    draw_ups: int = 0
    draw_downs: int = 0
    color_balance: int = 0

    def placement_criteria(self):
        return -self.mms_x2, -self.sos_x2, -self.sosos_x2, self.player_id
