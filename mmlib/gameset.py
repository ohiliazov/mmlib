from typing import Optional

from mmlib.game import Game


class GameSet(set[Game]):
    def get(self, game_id: str) -> Optional[Game]:
        for game in self:
            if game.game_id == game_id:
                return game
