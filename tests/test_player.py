import random

from mmlib.player import PlayerSet


def test_player(generated_players):
    player1, player2 = random.sample(generated_players, k=2)

    assert player1 != player2

    player2.player_id = player1.player_id
    assert player1 == player2


def test_player_set(generated_players):
    player_set = PlayerSet(generated_players)
    player = random.choice(generated_players)

    assert player_set.get(player.player_id) is player
    assert player_set.get("fake-uuid4") is None
