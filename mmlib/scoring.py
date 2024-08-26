from collections import defaultdict

from mmlib.models import Game, Player, ScoredPlayer


class GamesRepository:
    def __init__(self, games: list[list[Game]]) -> None:
        self.data = defaultdict(dict)

        for rn, round_games in enumerate(games):
            for game in round_games:
                self.data[rn][game.black_id] = game
                self.data[rn][game.white_id] = game

    def get_game(self, player_id: str, round_number: int) -> Game | None:
        return self.data[round_number].get(player_id)


def make_scored_players(
    players: list[Player], games: list[list[Game]]
) -> dict[str, ScoredPlayer]:
    games_repo = GamesRepository(games)
    result: dict[str, ScoredPlayer] = {
        player.player_id: ScoredPlayer.from_player(player)
        for player in players
    }

    for round_number in range(len(games)):
        scored_players = {}

        for player in players:
            player_id = player.player_id
            sp = result[player_id].model_copy()
            scored_players[player_id] = sp

            if sp.is_bye:
                # bye players don't get points
                continue

            if game := games_repo.get_game(player_id, round_number):
                opponent_id = game.opponent_id(player_id)
                opponent = result[opponent_id]

                if not opponent.is_bye:
                    if sp.score_x2 < opponent.score_x2:
                        sp.draw_ups += 1
                    if sp.score_x2 > opponent.score_x2:
                        sp.draw_downs += 1

                sp.points_x2 += game.points_x2(player_id)
                sp.mms_x2 = sp.get_mms_x2()
                sp.score_x2 = sp.get_score_x2()
                sp.sos_x2 += opponent.score_x2
                sp.sosos_x2 += opponent.sos_x2
                sp.color_balance += game.color_balance(player_id)
                sp.opponent_ids.add(opponent_id)
            else:
                sp.skipped_x2 += 1

        result = scored_players

    return result


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
