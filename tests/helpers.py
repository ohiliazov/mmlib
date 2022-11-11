import faker
from mmlib.player import Player
from mmlib.game import Game

fake = faker.Faker()


def generate_player():
    return Player(
        player_id=fake.uuid4(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        country=fake.country_code(),
        club=fake.city(),
        rank=fake.random_int(-30, 8),
    )


def generate_game(black_id: str = None, white_id: str = None) -> Game:
    if black_id is None:
        black_id = fake.uuid4()
    if white_id is None:
        white_id = fake.uuid4()
    return Game(
        game_id=fake.uuid4(),
        round_number=fake.random_int(0, 10),
        black_id=black_id,
        white_id=white_id,
        handicap=fake.random_int(0, 9),
    )
