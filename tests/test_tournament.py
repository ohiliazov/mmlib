from mmlib.parameters import HandicapParameters
from mmlib.tournament import Tournament


def test_make_game(generated_players):
    Tournament(
        handicap_params=HandicapParameters(
            handicap_bar=0,
            handicap_max=0,
            handicap_correction=0,
        )
    )
