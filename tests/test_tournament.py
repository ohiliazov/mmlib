import pytest

from mmlib.parameters import Parameters
from mmlib.tournament import Tournament


def test_make_game(generated_players):
    tournament = Tournament(parameters=Parameters())
