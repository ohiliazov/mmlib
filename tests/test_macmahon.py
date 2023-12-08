import json
from pathlib import Path

import pytest

from mmlib.macmahon import MacMahon
from mmlib.models import Game, Tournament

test_data_path = Path(__file__).parent / "test_data"


def get_input_paths():
    input_dir = test_data_path / "input"
    return [input_path.name for input_path in input_dir.iterdir()]


def load_data(name: str) -> tuple[Tournament, list[Game]]:
    input_dir = test_data_path / "input"
    output_dir = test_data_path / "output"

    with open(input_dir / name) as in_f, open(output_dir / name) as out_f:
        tournament = Tournament.model_validate_json(in_f.read())
        games = [Game.model_validate(item) for item in json.load(out_f)]
        return tournament, games


@pytest.mark.parametrize("name", get_input_paths())
def test_macmahon(name):
    tournament, expected = load_data(name)

    mm = MacMahon(tournament.players, tournament.games, tournament.parameters)

    for item in mm.make_pairing([p.player_id for p in tournament.players]):
        assert item in expected
