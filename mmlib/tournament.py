import random
import uuid
from typing import Iterable

from mmlib.game import Game, GameSet
from mmlib.parameters import HandicapParameters
from mmlib.player import Player, PlayerSet
from mmlib.handicap import calculate_handicap


class Tournament:
    def __init__(
        self,
        handicap_parameters: HandicapParameters,
        players: Iterable[Player] = None,
        games: Iterable[Game] = None,
    ):
        self.handicap_params = handicap_parameters
        self.players = PlayerSet(players or set())
        self.games = GameSet(games or set())

    def make_game(self, round_number: int, player1: Player, player2: Player) -> Game:
        if player1.rank > player2.rank:
            player1, player2 = player2, player1

        handicap = calculate_handicap(
            lower_rank=player1.rank,
            higher_rank=player2.rank,
            handicap_params=self.handicap_params,
        )
        p1_color_balance = self.games.color_balance(player1.player_id)
        p2_color_balance = self.games.color_balance(player2.player_id)

        if handicap or p1_color_balance > p2_color_balance:
            black_id, white_id = player1.player_id, player2.player_id
        elif p1_color_balance < p2_color_balance:
            white_id, black_id = player1.player_id, player2.player_id
        else:
            random.seed(f"{player1.player_id}::{player2.player_id}")
            black_id, white_id = random.sample(
                [player1.player_id, player2.player_id],
                k=2,
            )

        return Game(
            game_id=f"{round_number}::{white_id}::{black_id}",
            round_number=round_number,
            black_id=black_id,
            white_id=white_id,
            handicap=handicap,
        )
