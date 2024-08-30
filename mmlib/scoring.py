from mmlib.models import Game, Player, ScoredGame, ScoredPlayer


def make_scored_players(
    players: list[Player], all_games: list[list[Game]]
) -> dict[str, ScoredPlayer]:
    scored_players = {
        player.player_id: ScoredPlayer.from_player(player)
        for player in players
    }

    for round_games in all_games:
        next_scored_players = {
            player_id: scored_player.copy()
            for player_id, scored_player in scored_players.items()
        }

        scored_games = {}
        for game in round_games:
            scored_game = ScoredGame.from_game(
                game=game,
                black=scored_players[game.black_id],
                white=scored_players[game.white_id],
            )
            scored_games[game.black_id] = scored_game
            scored_games[game.white_id] = scored_game

        for player_id, sp in next_scored_players.items():
            if sg := scored_games.get(player_id):
                sp.color_balance += sg.color_balance(sp)
                sp.draw_ups += sg.draw_ups(sp)
                sp.draw_downs += sg.draw_downs(sp)
                sp.points += sg.points(sp)
                sp.score = sp.smms + int(sp.points + sp.skips / 2)
                sp.games.append(sg)
            else:
                sp.skips += 1
        scored_players = next_scored_players

    # MMS
    for player_id, sp in scored_players.items():
        sp.mms = sp.smms + int(sp.points)

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
