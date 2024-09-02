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
    result: GameResult = GameResult.UNKNOWN


class ScoredPlayer(Player):
    points: float = 0.0
    skips: int = 0
    draw_ups: int = 0
    draw_downs: int = 0
    sos: int = 0
    sosos: int = 0
    sodos: int = 0
    games: list["ScoredGame"] = Field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.player_id)

    def __eq__(self, other: "ScoredPlayer") -> bool:
        return self.player_id == other.player_id

    @classmethod
    def from_player(cls, player: Player) -> "ScoredPlayer":
        return cls(
            player_id=player.player_id,
            rank=player.rank,
            smms=player.smms,
        )

    def add_round(self, sg: "ScoredGame | None") -> "ScoredPlayer":
        if sg is None:
            return self.model_copy(update={"skips": self.skips + 1})
        return self.model_copy(
            update={
                "draw_ups": self.draw_ups + sg.draw_ups(self),
                "draw_downs": self.draw_downs + sg.draw_downs(self),
                "points": self.points + sg.points(self),
                "games": self.games + [sg],
            },
        )

    @property
    def mms(self) -> int:
        return self.smms + int(self.points)

    @property
    def score(self) -> int:
        return self.smms + int(self.points + self.skips / 2)

    @property
    def color_balance(self):
        return sum(game.color_balance(self) for game in self.games)


class ScoredGame(BaseModel):
    black: ScoredPlayer
    white: ScoredPlayer
    handicap: int
    result: GameResult

    @classmethod
    def from_game(
        cls, game: Game, black: ScoredPlayer, white: ScoredPlayer
    ) -> "ScoredGame":
        return ScoredGame(
            black=black,
            white=white,
            handicap=game.handicap,
            result=game.result,
        )

    def _verify_player(self, player: ScoredPlayer) -> None:
        if player not in (self.black, self.white):
            raise ValueError(f"Player {player} is not black or white.")

    def is_black(self, player: ScoredPlayer) -> bool:
        return self.black == player

    def is_white(self, player: ScoredPlayer) -> bool:
        return self.white == player

    def points(self, player: ScoredPlayer) -> float:
        self._verify_player(player)

        if player.is_bye:
            return 0

        if self.opponent(player).is_bye:
            return 1

        match self.result:
            case GameResult.WHITE_WINS if self.is_white(player):
                return 1
            case GameResult.BLACK_WINS if self.is_black(player):
                return 1
            case GameResult.DRAW:
                return 0.5
        return 0

    def opponent(self, player: ScoredPlayer) -> ScoredPlayer:
        self._verify_player(player)
        return self.black if self.is_white(player) else self.white

    def color_balance(self, player: ScoredPlayer) -> int:
        self._verify_player(player)

        if self.black.is_bye or self.white.is_bye or self.handicap:
            return 0

        return -1 if self.black == player else 1

    def draw_ups(self, player: ScoredPlayer) -> int:
        self._verify_player(player)

        if self.black.is_bye or self.white.is_bye:
            return 0

        return int(player.score < self.opponent(player).score)

    def draw_downs(self, player: ScoredPlayer) -> int:
        self._verify_player(player)

        if self.black.is_bye or self.white.is_bye:
            return 0

        return int(player.score > self.opponent(player).score)


class Tournament(BaseModel):
    players: list[Player]
    games: list[list[Game]]
    parameters: Parameters
