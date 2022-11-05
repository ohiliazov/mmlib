from typing import Optional

from mmlib.player import Player


class PlayerSet(set[Player]):
    def get(self, player_id: str) -> Optional[Player]:
        for player in self:
            if player.player_id == player_id:
                return player
