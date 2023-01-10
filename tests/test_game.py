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


def test_game_set_color_balance(generated_players):
    game_set = GameSet()
    player1, player2 = random.sample(generated_players, k=2)

    # playing as white increases color balance
    game_set.add(
        Game(
            game_id="game1",
            round_number=0,
            black_id=player1.player_id,
            white_id=player2.player_id,
            handicap=0,
        )
    )
    assert game_set.color_balance(player1.player_id) == -1
    assert game_set.color_balance(player2.player_id) == 1

    # handicap games should not be included in color balance count
    game_set.add(
        Game(
            game_id="game2",
            round_number=0,
            black_id=player2.player_id,
            white_id=player1.player_id,
            handicap=1,
        )
    )
    assert game_set.color_balance(player1.player_id) == -1
    assert game_set.color_balance(player2.player_id) == 1

    game_set.add(
        Game(
            game_id="game3",
            round_number=0,
            black_id=player2.player_id,
            white_id=player1.player_id,
            handicap=0,
        )
    )
    assert game_set.color_balance(player1.player_id) == 0
    assert game_set.color_balance(player2.player_id) == 0
