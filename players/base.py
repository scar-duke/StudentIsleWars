from __future__ import annotations

from abc import ABC, abstractmethod

from game.models import GameState


class PlayerController(ABC):
    def __init__(self, player_id: int, player_name: str, file_name: str = ""):
        self.player_id = player_id
        self.player_name = player_name
        self.rules_file = ""
        if file_name != "":
            self.rules_file = file_name
        # only used for "remembering" reinforcement requests for ASP players
        self.reinforcement_moves = []
        

    @abstractmethod
    def choose_action(self, state: GameState):
        pass
