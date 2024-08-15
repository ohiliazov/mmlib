import itertools
import random
from typing import Iterator

import networkx as nx

from mmlib.constants import FloatingMode, Weight
from mmlib.floating import floating_coefficient
from mmlib.handicap import calculate_handicap
from mmlib.models import Game, Parameters, Player, ScoredPlayer
from mmlib.seeding import seeding_coefficient


class GamesRepository:
    def __init__(self, games: list[list[Game]]):
        self.data = games

    def __len__(self) -> int:
        return len(self.data)

    def _player_games(self, player_id: str) -> Iterator[Game]:
        return (
            game
            for game in itertools.chain(*self.data)
            if game.has_played(player_id)
        )

    def game_in_round(self, player_id: str, round_number: int) -> Game | None:
        for game in self.data[round_number]:
            if game.has_played(player_id):
                return game

    def have_played(self, player1_id: str, player2_id: str):
        return any(
            game.has_played(player2_id)
            for game in self._player_games(player1_id)
        )


class ScoresRepository:
    def __init__(
        self,
        players: list[Player],
        games: list[list[Game]],
    ):
        games_repo = GamesRepository(games)
        self.data: dict[str, ScoredPlayer] = {
            player.player_id: ScoredPlayer(
                player_id=player.player_id,
                rank=player.rank,
                smms_x2=player.smms_x2,
            )
            for player in players
        }

        for rn in range(1, len(games_repo) + 1):
            scored_players = {}

            for player in players:
                player_id = player.player_id
                sp = self.data[player_id].model_copy()

                if game := games_repo.game_in_round(player_id, rn - 1):
                    opponent_id = game.opponent_id(player_id)
                    op = self.data[opponent_id]

                    if sp.score_x2 < op.score_x2:
                        sp.draw_ups += 1
                    if sp.score_x2 > op.score_x2:
                        sp.draw_downs += 1

                    sp.points_x2 += game.points_x2(player_id)
                    sp.sos_x2 += op.score_x2
                    sp.sosos_x2 += op.sos_x2
                    sp.color_balance += game.color_balance(player_id)
                    sp.opponent_ids.add(opponent_id)
                else:
                    sp.skipped_x2 += 1

                scored_players[player_id] = sp

            self.data = scored_players

        self.score_groups = self._make_score_groups()

    def __getitem__(self, item: str) -> ScoredPlayer:
        return self.data[item]

    def _make_score_groups(self) -> list[int]:
        return sorted({sp.score_x2 for sp in self.data.values()}, reverse=True)

    def score_group(self, score_x2: int) -> list[ScoredPlayer]:
        return sorted(
            [
                scored_player
                for scored_player in self.data.values()
                if scored_player.score_x2 == score_x2
            ],
            key=lambda sp: sp.placement_criteria(),
        )

    def have_played(self, player1_id: str, player2_id: str):
        return player2_id in self.data[player1_id].opponent_ids


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
        if not self.scores.have_played(sp1.player_id, sp2.player_id):
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

        p1_group = score_groups.index(sp1.score_x2)
        p2_group = score_groups.index(sp2.score_x2)

        x = abs(p1_group - p2_group) / len(score_groups)
        return (1 - x) * (1 + x / 2) * Weight.score_weight.value

    def balance_seeding_cost(
        self,
        sp1: ScoredPlayer,
        sp2: ScoredPlayer,
    ) -> float:
        if sp1.score_x2 == sp2.score_x2:
            k = self._seeding_coefficient(sp1, sp2)
            return k * Weight.seeding_weight.value

        if abs(sp1.score_x2 - sp2.score_x2) > 3:
            return 0

        if sp1.score_x2 > sp2.score_x2:
            sp1, sp2 = sp2, sp1

        scenario_coef = self._dudd_scenario(sp1, sp2)
        float_up_coef = self._floating_coef(sp1, self.parameters.float_up_mode)
        float_down_coef = self._floating_coef(
            sp2, self.parameters.float_down_mode
        )

        k = (scenario_coef + float_up_coef + float_down_coef) / 10

        return k * Weight.dudd_weight.value

    def _seeding_coefficient(self, sp1: ScoredPlayer, sp2: ScoredPlayer):
        score_group = self.scores.score_group(sp1.score_x2)

        p1_idx = score_group.index(sp1)
        p2_idx = score_group.index(sp2)
        group_size = len(score_group)
        mode = self.parameters.seeding_mode

        return seeding_coefficient(p1_idx, p2_idx, group_size, mode)

    def _floating_coef(self, sp: ScoredPlayer, mode: FloatingMode):
        score_group = self.scores.score_group(sp.score_x2)

        place = score_group.index(sp)
        size = len(score_group)

        return floating_coefficient(mode, place, size)

    def _dudd_scenario(self, sp1: ScoredPlayer, sp2: ScoredPlayer) -> int:
        scenario = 2  # normal conditions
        if sp1.draw_ups:
            scenario -= 1  # avoid drawing up the same player
        if sp2.draw_downs:
            scenario -= 1  # avoid drawing down the same player

        if scenario > 0:
            if sp1.draw_ups < sp1.draw_downs:
                scenario += 1  # correct draw-ups for sp1
            if sp2.draw_downs < sp2.draw_ups:
                scenario += 1  # correct draw-downs for sp2

        if scenario > 2 and not self.parameters.dudd_compensate:
            scenario = 2

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
