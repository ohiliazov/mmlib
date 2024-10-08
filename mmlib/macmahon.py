import itertools
import random

import networkx as nx

from mmlib.constants import FloatingMode, Weight
from mmlib.floating import floating_coefficient
from mmlib.handicap import calculate_handicap
from mmlib.models import Game, Parameters, Player, ScoredPlayer
from mmlib.scoring import ScoresRepository
from mmlib.seeding import seeding_coefficient


class MacMahon:
    def __init__(
        self,
        players: list[Player],
        games: list[list[Game]],
        parameters: Parameters,
    ):
        self.scores = ScoresRepository(players, games)
        self.parameters = parameters

    def make_pairing(self, to_match: list[str]) -> list[Game]:
        assert len(to_match) % 2 == 0

        graph = nx.Graph()

        for p1, p2 in itertools.combinations(to_match, 2):
            cost = self.calculate_cost(p1, p2)
            graph.add_edge(p1, p2, weight=cost)

        return sorted(
            [
                self.make_game(sp1=self.scores[p1_id], sp2=self.scores[p2_id])
                for p1_id, p2_id in nx.max_weight_matching(
                    graph, maxcardinality=True
                )
            ],
            key=lambda game: game.black_id,
        )

    def calculate_cost(self, player1_id: str, player2_id: str) -> float:
        sp1 = self.scores[player1_id]
        sp2 = self.scores[player2_id]

        cost = 1
        cost += self.unique_game_cost(sp1, sp2)
        cost += self.balance_color_cost(sp1, sp2)
        cost += self.score_difference_cost(sp1, sp2)
        cost += self.balance_seeding_cost(sp1, sp2)
        return cost

    def unique_game_cost(self, sp1: ScoredPlayer, sp2: ScoredPlayer) -> int:
        if not self.scores.have_played(sp1, sp2):
            return Weight.unique_game_weight.value
        return 0

    def balance_color_cost(
        self, sp1: ScoredPlayer, sp2: ScoredPlayer
    ) -> float:
        if self.make_game(sp1, sp2).handicap:
            return 0

        p1_cb = sp1.color_balance
        p2_cb = sp2.color_balance

        if p1_cb * p2_cb < 0:
            # color balance corrected for both players
            k = 1
        elif p1_cb * p2_cb == 0 and (p1_cb > 1 or p2_cb > 1):
            # color balance corrected for one player
            k = 0.5
        else:
            k = 0

        return k * Weight.color_weight.value

    def score_difference_cost(
        self,
        sp1: ScoredPlayer,
        sp2: ScoredPlayer,
    ) -> float:
        score_groups = self.scores.score_groups

        p1_group = score_groups.index(sp1.score)
        p2_group = score_groups.index(sp2.score)

        x = abs(p1_group - p2_group) / len(score_groups)
        return (1 - x) * (1 + x / 2) * Weight.score_weight.value

    def balance_seeding_cost(
        self,
        sp1: ScoredPlayer,
        sp2: ScoredPlayer,
    ) -> float:
        if sp1.score == sp2.score:
            k = self._seeding_coefficient(sp1, sp2)
            return k * Weight.seeding_weight.value

        if abs(sp1.score - sp2.score) >= 1.5:
            return 0

        if sp1.score > sp2.score:
            sp1, sp2 = sp2, sp1

        scenario_coef = self._dudd_scenario(sp1, sp2)
        float_up_coef = self._floating_coef(sp1, self.parameters.float_up_mode)
        float_down_coef = self._floating_coef(
            sp2, self.parameters.float_down_mode
        )

        k = (scenario_coef + float_up_coef + float_down_coef) / 10

        return k * Weight.dudd_weight.value

    def _seeding_coefficient(self, sp1: ScoredPlayer, sp2: ScoredPlayer):
        score_group = self.scores.score_group(sp1.score)

        p1_idx = score_group.index(sp1)
        p2_idx = score_group.index(sp2)
        group_size = len(score_group)
        mode = self.parameters.seeding_mode

        return seeding_coefficient(p1_idx, p2_idx, group_size, mode)

    def _floating_coef(self, sp: ScoredPlayer, mode: FloatingMode):
        score_group = self.scores.score_group(sp.score)

        place = score_group.index(sp)
        size = len(score_group)

        return floating_coefficient(mode, place, size)

    def _dudd_scenario(self, sp1: ScoredPlayer, sp2: ScoredPlayer) -> int:
        scenario = 2  # normal conditions
        if sp1.draw_ups:
            scenario -= 1  # avoid drawing up the same player
        if sp2.draw_downs:
            scenario -= 1  # avoid drawing down the same player

        if scenario != 0 and self.parameters.dudd_compensate:
            if sp1.draw_ups < sp1.draw_downs:
                scenario += 1  # correct draw-ups for sp1
            if sp2.draw_downs < sp2.draw_ups:
                scenario += 1  # correct draw-downs for sp2

        return scenario * 2

    def make_game(self, sp1: ScoredPlayer, sp2: ScoredPlayer) -> Game:
        if sp1.rank > sp2.rank:
            sp1, sp2 = sp2, sp1

        handicap = calculate_handicap(
            r1=sp1.rank,
            r2=sp2.rank,
            hd_bar=self.parameters.hd_bar,
            hd_adj=self.parameters.hd_adj,
            hd_max=self.parameters.hd_max,
        )

        if handicap or sp1.color_balance > sp2.color_balance:
            black_id, white_id = sp1.player_id, sp2.player_id
        elif sp1.color_balance < sp2.color_balance:
            black_id, white_id = sp2.player_id, sp1.player_id
        else:
            random.seed((sp1.player_id + sp2.player_id))
            black_id, white_id = random.sample(
                [sp1.player_id, sp2.player_id],
                k=2,
            )

        return Game(
            black_id=black_id,
            white_id=white_id,
            handicap=handicap,
        )
