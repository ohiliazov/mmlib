class Player:
    def __init__(
        self,
        player_id: str,
        first_name: str,
        last_name: str,
        country: str,
        club: str,
        rank: int,
    ):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.country = country
        self.club = club
        self.rank = rank

    def __repr__(self):
        return f"Player({self.player_id=}, {self.first_name=}, {self.last_name=})"

    def __str__(self):
        return repr(self)

    def __eq__(self, other: "Player"):
        return self.player_id == other.player_id

    def __hash__(self):
        return hash(self.player_id)
