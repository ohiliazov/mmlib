from mmlib.models import Game, Player, ScoredGame, ScoredPlayer


def make_scored_players(
    players: list[Player], all_games: list[list[Game]]
) -> dict[str, ScoredPlayer]:
    scored_players = {
        player.player_id: ScoredPlayer.from_player(player)
        for player in players
    }

    for round_games in all_games:
        scored_games = {}
        for game in round_games:
            scored_game = ScoredGame.from_game(
                game=game,
                black=scored_players[game.black_id],
                white=scored_players[game.white_id],
            )
            scored_games[game.black_id] = scored_game
            scored_games[game.white_id] = scored_game

        next_scored_players = {}
        for player_id, sp in scored_players.items():
            sg = scored_games.get(player_id)
            next_scored_players[player_id] = sp.add_round(sg)

        scored_players = next_scored_players

    # SOS
    for player_id, sp in scored_players.items():
        for game in sp.games:
            opponent = scored_players[game.opponent(sp).player_id]
            if opponent.is_bye:
                sp.sos += sp.score
                if game.points(sp) == 2:
                    sp.sodos += sp.score
            else:
                sp.sos += opponent.score
                if game.points(sp) == 2:
                    sp.sodos += sp.score

    # SOSOS
    for player_id, sp in scored_players.items():
        for game in sp.games:
            opponent = scored_players[game.opponent(sp).player_id]
            if opponent.is_bye:
                sp.sosos += sp.sos
            else:
                sp.sosos += opponent.sos

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

    def have_played(self, sp1: ScoredPlayer, sp2: ScoredPlayer):
        return any(sg.opponent(sp1) == sp2 for sg in sp1.games)
