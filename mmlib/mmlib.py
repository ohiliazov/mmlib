import dataclasses
import itertools
from enum import IntEnum, StrEnum
from typing import Iterator

import networkx as nx


# fmt: off
class Weight(IntEnum):
    unique_game_weight = 500_000_000_000_000
    score_weight =           100_000_000_000
    dudd_weight =                100_000_000
    seeding_weight =               5_000_000
    color_weight =                 1_000_000
# fmt:on


class GameResult(StrEnum):
    UNKNOWN = "unknown"
    BOTH_WIN = "both_wins"
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW = "draw"
    BOTH_LOSE = "both_lose"


class DUDDMode(StrEnum):
    """
    If set to TOP the first player will be prioritised to be drawn up/down.
    If set to MIDDLE the middle player will be prioritised to drawn up/down.
    If set to BOTTOM the last player will be prioritised to drawn up/down.
    """

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class SeedingMode(StrEnum):
    """
    If set to CROSS the first player will be seeded with middle.
    If set to FOLD the first player will be seeded with last.
    If set to ADJACENT the first player will be seeded with second, third with fourth etc.
    """

    CROSS = "cross"
    FOLD = "fold"
    ADJACENT = "adjacent"


@dataclasses.dataclass
class Parameters:
    hd_bar: int = 0
    hd_correction: int = 0
    hd_maximum: int = 0
    dudd_compensate: bool = True
    du_mode: DUDDMode = DUDDMode.MIDDLE
    dd_mode: DUDDMode = DUDDMode.MIDDLE
    seeding_mode: SeedingMode = SeedingMode.CROSS


@dataclasses.dataclass
class PlayerInfo:
    player_id: str
    rank: int
    smms_x2: int


@dataclasses.dataclass
class GameInfo:
    black_id: str
    white_id: str
    round_number: int
    handicap: int
    result: GameResult = GameResult.UNKNOWN

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


@dataclasses.dataclass
class ScoredPlayer(PlayerInfo):
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


def concave(x: float) -> float:
    return (1 - x) * (1 + x / 2)


class GamesRepository:
    def __init__(self, games: set[GameInfo]):
        self.games = games

    def games_before_round(
        self, player_id: str, round_number: int
    ) -> Iterator[GameInfo]:
        for game in self.games:
            if game.round_number < round_number and game.has_played(player_id):
                yield game

    def game_in_round(
        self, player_id: str, round_number: int
    ) -> GameInfo | None:
        for game in self.games:
            if game.round_number == round_number and game.has_played(
                player_id
            ):
                return game


class PairingMaker:
    def __init__(
        self,
        players: dict[str, PlayerInfo],
        games: set[GameInfo],
        parameters: Parameters,
    ):
        self.players = players
        self.games = GamesRepository(games)
        self.parameters = parameters
        self._scored_players: list[dict[str, ScoredPlayer]] = []

    def _make_scored_players(self, round_number: int):
        scored_players = []

        for rn in range(round_number + 1):
            rn_scored_players = {}
            for player_id, player in self.players.items():
                sp = ScoredPlayer(
                    player_id=player.player_id,
                    rank=player.rank,
                    smms_x2=player.smms_x2,
                )

                if rn > 0:
                    prev_sp = scored_players[rn - 1][player_id]
                    sp.points_x2 = prev_sp.points_x2
                    sp.skipped_x2 = prev_sp.skipped_x2
                    sp.sos_x2 = prev_sp.sos_x2
                    sp.sosos_x2 = prev_sp.sosos_x2

                    sp.draw_ups = prev_sp.draw_ups
                    sp.draw_downs = prev_sp.draw_downs

                    if game := self.games.game_in_round(player_id, rn - 1):
                        opponent_id = game.opponent_id(player_id)
                        prev_op = scored_players[rn - 1][opponent_id]

                        sp.points_x2 += game.points_x2(player_id)
                        sp.sos_x2 += prev_op.score_x2
                        sp.sosos_x2 += prev_op.sos_x2

                        if prev_sp.score_x2 < prev_op.score_x2:
                            sp.draw_ups += 1
                        if prev_sp.score_x2 > prev_op.score_x2:
                            sp.draw_downs += 1

                    else:
                        sp.skipped_x2 += 1

                rn_scored_players[player_id] = sp

            scored_players.append(rn_scored_players)

        self._scored_players = scored_players

    def make_pairing(
        self, rn: int, to_match: list[str]
    ) -> set[tuple[str, str]]:
        assert len(to_match) % 2 == 0

        self._make_scored_players(rn)

        graph = nx.Graph()

        for p1, p2 in itertools.combinations(to_match, 2):
            cost = self.calculate_cost(rn, p1, p2)
            graph.add_edge(p1, p2, weight=cost)

        return nx.max_weight_matching(graph, maxcardinality=True)

    def calculate_cost(
        self,
        rn: int,
        player1_id: str,
        player2_id: str,
    ) -> float:
        sp1 = self._scored_players[rn][player1_id]
        sp2 = self._scored_players[rn][player2_id]

        cost = 1
        cost += self.unique_game_cost(rn, player1_id, player2_id)
        cost += self.balance_color_cost(rn, sp1, sp2)
        cost += self.score_difference_cost(rn, sp1, sp2)
        cost += self.balance_seeding_cost(rn, sp1, sp2)

        return cost

    def unique_game_cost(
        self, rn: int, player1_id: str, player2_id: str
    ) -> int:
        if self._has_played(rn, player1_id, player2_id):
            return Weight.unique_game_weight.value
        return 0

    def _has_played(self, rn: int, player1_id: str, player2_id: str):
        return any(
            game.has_played(player2_id)
            for game in self.games.games_before_round(player1_id, rn)
        )

    def balance_color_cost(
        self, rn: int, sp1: ScoredPlayer, sp2: ScoredPlayer
    ) -> float:
        if self._calculate_handicap(sp1.rank, sp2.rank):
            return 0

        p1_cb = self._calculate_color_balance(sp1.player_id, rn)
        p2_cb = self._calculate_color_balance(sp2.player_id, rn)

        if p1_cb * p2_cb < 0:
            # color balance corrected for both players
            k = 1
        elif p1_cb * p2_cb == 0 and abs(p1_cb + p2_cb) > 1:
            # color balance corrected for one of the players
            k = 0.5
        else:
            k = 0
        return k * Weight.color_weight.value

    def _calculate_handicap(self, sp1_rank: int, sp2_rank: int) -> int:
        sp1_handicap_rank = max(sp1_rank, self.parameters.hd_bar)
        sp2_handicap_rank = max(sp2_rank, self.parameters.hd_bar)

        base_handicap = abs(sp1_handicap_rank - sp2_handicap_rank)
        corrected_handicap = base_handicap + self.parameters.hd_correction

        return min(max(corrected_handicap, 0), self.parameters.hd_maximum)

    def _calculate_color_balance(self, player_id: str, rn: int) -> int:
        balance = 0
        for game in self.games.games_before_round(player_id, rn):
            if game.handicap == 0:
                if game.white_id == player_id:
                    balance += 1
                else:
                    balance -= 1
        return balance

    def score_difference_cost(
        self,
        rn: int,
        sp1: ScoredPlayer,
        sp2: ScoredPlayer,
    ) -> float:
        score_x2_list = sorted(
            {sp.score_x2 for sp in self._scored_players[rn].values()}
        )

        p1_group = score_x2_list.index(sp1.score_x2)
        p2_group = score_x2_list.index(sp2.score_x2)

        k = concave(abs(p1_group - p2_group) / len(score_x2_list))

        return k * Weight.score_weight.value

    def balance_seeding_cost(
        self,
        rn: int,
        sp1: ScoredPlayer,
        sp2: ScoredPlayer,
    ) -> float:
        if sp1.score_x2 == sp2.score_x2:
            k = self._seeding_coefficient(rn, sp1, sp2)
            return k * Weight.seeding_weight.value

        if abs(sp1.score_x2 - sp2.score_x2) > 3:
            return 0

        if sp1.score_x2 > sp2.score_x2:
            sp1, sp2 = sp2, sp1

        scenario_coef = self._dudd_scenario(sp1, sp2)
        du_coef = self._dudd_coefficient(rn, sp1, self.parameters.du_mode)
        dd_coef = self._dudd_coefficient(rn, sp2, self.parameters.dd_mode)
        dudd_coef = (du_coef + dd_coef) / 2

        k = (scenario_coef + dudd_coef) / 5
        return k * Weight.dudd_weight.value

    def _sorted_score_group(
        self, rn: int, score_x2: int
    ) -> list[ScoredPlayer]:
        players_in_group = [
            sp
            for sp in self._scored_players[rn].values()
            if sp.score_x2 == score_x2
        ]

        def placement_criteria(sp: ScoredPlayer):
            return sp.mms_x2, sp.sos_x2, sp.sosos_x2

        return sorted(players_in_group, key=placement_criteria, reverse=True)

    def _dudd_coefficient(self, rn: int, sp: ScoredPlayer, mode: DUDDMode):
        score_group = self._sorted_score_group(rn, sp.score_x2)

        place = score_group.index(sp)
        last = len(score_group) - 1

        if last == 0:
            return 1

        match mode:
            case DUDDMode.BOTTOM:
                return place / last

            case DUDDMode.TOP:
                return 1 - place / last

            case DUDDMode.MIDDLE:
                mid = last // 2
                place = last - place if place > mid else place
                return place / mid

        return 0

    def _dudd_scenario(self, sp1: ScoredPlayer, sp2: ScoredPlayer) -> int:
        scenario = 2  # normal conditions
        if sp1.draw_ups:
            scenario -= 1  # increases weaker participant draw-ups
        if sp2.draw_downs:
            scenario -= 1  # increases strong participant draw-downs

        if scenario > 0:  # if not the worst case
            if sp1.draw_ups < sp1.draw_downs:
                scenario += 1  # corrects weaker participant draw-ups
            if sp2.draw_downs < sp2.draw_ups:
                scenario += 1  # corrects strong participant draw-downs

        if scenario > 2 and not self.parameters.dudd_compensate:
            scenario = 2
        return scenario

    def _seeding_coefficient(
        self, rn: int, sp1: ScoredPlayer, sp2: ScoredPlayer
    ):
        score_group = self._sorted_score_group(rn, sp1.score_x2)

        p1_idx = score_group.index(sp1)
        p2_idx = score_group.index(sp2)
        size = len(score_group)

        term = 0
        match self.parameters.seeding_mode:
            case SeedingMode.CROSS if size > 3:
                term = abs(2 * abs(p1_idx - p2_idx) - size)
            case SeedingMode.FOLD if size > 2:
                term = abs(p2_idx + p1_idx - size + 1)
            case SeedingMode.ADJACENT if size > 2:
                term = abs(p1_idx - p2_idx) - 1

        return 1 - term / (size - 2)
