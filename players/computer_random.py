from __future__ import annotations

import random

from game.actions import AttackAction, EndPhaseAction, PlaceArmiesAction
from game.models import GameState, Phase
from game.rules import get_territories_owned_by, get_valid_attacks
from players.base import PlayerController


class RandomComputerPlayer(PlayerController):
    def choose_action(self, state: GameState):
        # if we have no territories, we have been defeated, and will skip our turn
        if len(get_territories_owned_by(state, self.player_id)) == 0:
            return EndPhaseAction()

        if state.current_phase == Phase.REINFORCE:
            return self._choose_reinforcement(state)
        return self._choose_attack_or_end(state)

    def _choose_reinforcement(self, state: GameState) -> PlaceArmiesAction:
        owned = get_territories_owned_by(state, self.player_id)
        territory = random.choice(owned)
        count = state.reinforcements_remaining
        return PlaceArmiesAction(territory, count)

    def _choose_attack_or_end(self, state: GameState):
        attacks = get_valid_attacks(state, self.player_id)
        if len(attacks) == 0:
            return EndPhaseAction()
        if random.random() < 0.10:
            return EndPhaseAction()
        source, target = random.choice(attacks)
        return AttackAction(source, target)
