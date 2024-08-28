from collections import defaultdict

from mmlib.models import Game, Player, ScoredPlayer


def make_scored_players(
    players: list[Player], all_games: list[list[Game]]
) -> dict[str, ScoredPlayer]:
    scored_players: dict[str, ScoredPlayer] = {
        player.player_id: ScoredPlayer.from_player(player)
        for player in players
    }

    for round_games in all_games:
        skipped_player_ids = set(scored_players)
        for game in round_games:
            black_id = game.black_id
            white_id = game.white_id

            black = scored_players[black_id]
            white = scored_players[white_id]

            if not black.is_bye and not white.is_bye:
                black.color_balance += game.color_balance(black_id)
                white.color_balance += game.color_balance(white_id)

                if black.score < white.score:
                    black.draw_ups += 1
                    white.draw_downs += 1
                elif black.score > white.score:
                    black.draw_downs += 1
                    white.draw_ups += 1

            if not black.is_bye:
                black.points += game.points(black_id)

            if not white.is_bye:
                white.points += game.points(white_id)

            skipped_player_ids -= {black_id, white_id}

            black.opponent_ids.add(white_id)
            white.opponent_ids.add(black_id)

        for skipped_player_id in skipped_player_ids:
            skipped_player = scored_players[skipped_player_id]
            skipped_player.skips += 1

    return scored_players


class ScoresRepository:
    def __init__(
        self,
        players: list[Player],
        games: list[list[Game]],
    ):
        self.data = make_scored_players(players, games)
        self.score_groups = self._make_score_groups()
        self.sos_scores = self._make_sos_scores()
        self.sosos_scores = self._make_sosos_scores()

    def __getitem__(self, item: str) -> ScoredPlayer:
        return self.data[item]

    def _make_score_groups(self) -> list[int]:
        return sorted({sp.score for sp in self.data.values()}, reverse=True)

    def _make_sos_scores(self) -> dict[str, int]:
        sos_scores = defaultdict(int)
        for player_id, scored_player in self.data.items():
            for opponent_id in scored_player.opponent_ids:
                opponent = self.data[opponent_id]
                if opponent.is_bye:
                    sos_scores[player_id] += scored_player.score
                else:
                    sos_scores[player_id] += opponent.score
        return sos_scores

    def _make_sosos_scores(self) -> dict[str, int]:
        sosos_scores = defaultdict(int)
        for player_id, scored_player in self.data.items():
            for opponent_id in scored_player.opponent_ids:
                opponent = self.data[opponent_id]
                if opponent.is_bye:
                    sosos_scores[player_id] += self.sos_scores[player_id]
                else:
                    sosos_scores[player_id] += self.sos_scores[opponent_id]
        return sosos_scores

    def score_group(self, score: int) -> list[ScoredPlayer]:
        return sorted(
            [
                scored_player
                for scored_player in self.data.values()
                if scored_player.score == score
            ],
            key=lambda sp: (-sp.mms, -sp.rank),
            reverse=True,
        )

    def have_played(self, player1_id: str, player2_id: str):
        return player2_id in self.data[player1_id].opponent_ids
