import json
from pathlib import Path
from typing import Iterator

import pytest

test_data_path = Path(__file__).parent / "test_data"


def load_data() -> Iterator[tuple[dict, dict]]:
    input_dir = test_data_path / "input"
    output_dir = test_data_path / "output"

    for input_path in input_dir.iterdir():
        output_path = output_dir / input_path.name

        with open(input_path) as in_f, open(output_path) as out_f:
            yield json.load(in_f), json.load(out_f)


@pytest.mark.parametrize("input, output", load_data())
def test_macmahon(input, output):
    print()
    print(input)
    print(output)
