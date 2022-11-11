import random

import faker
from mmlib.game import Game, GameSet
from tests.helpers import generate_game

fake = faker.Faker()


def test_game(generated_games):
    game1, game2 = random.sample(generated_games, k=2)
    game2 = generate_game()

    assert game1 != game2

    game2.game_id = game1.game_id
    assert game1 == game2


def test_game_set(generated_games):
    game_set = GameSet(generated_games)
    game1 = random.choice(generated_games)

    assert game_set.get(game1.game_id) is game1
    assert game_set.get("fake-uuid4") is None
