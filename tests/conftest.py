import random

import pytest
from tests.helpers import generate_player, generate_game
from mmlib.player import Player
from mmlib.game import Game


@pytest.fixture
def generated_players() -> list[Player]:
    return [generate_player() for _ in range(32)]


@pytest.fixture
def generated_games(generated_players) -> list[Game]:
    games = []
    for _ in range(32):
        black, white = random.sample(generated_players, k=2)
        games.append(generate_game(black_id=black.player_id, white_id=white.player_id))
    return games
