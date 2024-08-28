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

    def __getitem__(self, item: str) -> ScoredPlayer:
        return self.data[item]

    def _make_score_groups(self) -> list[int]:
        return sorted({sp.score for sp in self.data.values()}, reverse=True)

    def sos(self, sp: ScoredPlayer) -> int:
        return sum(
            self.data[opponent_id].score
            if not self.data[opponent_id].is_bye
            else sp.score - 1
            for opponent_id in sp.opponent_ids
        )

    def score_group(self, score: int) -> list[ScoredPlayer]:
        return sorted(
            [
                scored_player
                for scored_player in self.data.values()
                if scored_player.score == score
            ],
            key=lambda sp: (sp.score, sp.rank),
        )

    def have_played(self, player1_id: str, player2_id: str):
        return player2_id in self.data[player1_id].opponent_ids
