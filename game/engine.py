from __future__ import annotations

import random
from asp.generate_information import create_world_information
from game.actions import AttackAction, ConquerAction, MoveAction, EndPhaseAction, PlaceArmiesAction
from game.models import ActionResult, GameState, Phase
from game.rules import (
    get_territories_owned_by,
    calculate_reinforcements,
    can_attack,
    can_place_armies,
    get_valid_attacks,
    can_move,
    has_player_won,
)


class GameEngine:
    def __init__(self, state: GameState):
        self.state = state
        create_world_information(state.territories.values())

    def apply_action(self, action) -> ActionResult:
        player_id = self.state.current_player_id

        if isinstance(action, PlaceArmiesAction):
            return self._apply_place_armies(action, player_id)
        if isinstance(action, AttackAction):
            return self._apply_attack(action, player_id)
        if isinstance(action, ConquerAction):
            return self._apply_conquer(action, player_id)
        if isinstance(action, MoveAction):
            return self._apply_move(action, player_id)
        if isinstance(action, EndPhaseAction):
            return self._apply_end_phase()
        return ActionResult(False, "Unknown action type.")

    def is_game_over(self) -> bool:
        for player in self.state.players:
            if has_player_won(self.state, player.player_id):
                return True
        return False

    def winning_player_id(self) -> int | None:
        for player in self.state.players:
            if has_player_won(self.state, player.player_id):
                return player.player_id
        return None

    def _apply_place_armies(
        self,
        action: PlaceArmiesAction,
        player_id: int,
    ) -> ActionResult:
        if not can_place_armies(
            self.state,
            player_id,
            action.territory_name,
            action.count,
        ):
            return ActionResult(False, "Illegal reinforcement action.")
        territory = self.state.territories[action.territory_name]
        territory.armies += action.count
        self.state.reinforcements_remaining -= action.count
        if self.state.reinforcements_remaining == 0:
            self.state.current_phase = Phase.CHOOSE
        return ActionResult(True, self._place_message(action))

    def _apply_attack(
        self,
        action: AttackAction,
        player_id: int,
    ) -> ActionResult:
        if not can_attack(
            self.state,
            player_id,
            action.source_name,
            action.target_name,
        ):
            return ActionResult(False, "Illegal attack action.")
        source = self.state.territories[action.source_name]
        target = self.state.territories[action.target_name]
        self.state.last_attack_source = source
        self.state.last_attack_target = target

        # begin attack checks (roll two die)
        src_chance = random.randint(1, 6)
        trg_chance = random.randint(1, 6)

        # compare chances to see who "wins"
        win = True if src_chance > trg_chance else False
        #win = True if random.randint(1, 10) <= 3 else False

        # if successful conquering takes place (target had 1 and now has 0), update board
        if win and target.armies == 1:
            self.state.current_phase = Phase.CONQUER
            return ActionResult(True, "Conquered")
        # if won but not conquered
        if win:
            target.armies -= 1
            return ActionResult(True, self._win_message(action, source, target))
        
        # lost
        source.armies -= 1
        # if we were defeated (fought 2 against X and lost, so 1 left), target conquers
        if source.armies == 1:
            source.owner_id = target.owner_id
            self._advance_turn()
        return ActionResult(True, self._lose_message(action, source, target))

    def _apply_conquer(
        self,
        action: ConquerAction,
        player_id: int,
    ) -> ActionResult:
        source = self.state.last_attack_source
        target = self.state.last_attack_target
        last_owner = target.owner_id
        target.owner_id = player_id

        if not can_move(
            self.state,
            player_id,
            source.name,
            target.name,
            action.count,
        ):
            target.owner_id = last_owner
            return ActionResult(False, "Illegal conquer action.")

        source.armies -= action.count
        target.armies = action.count
        self.state.current_phase = Phase.CHOOSE
        return ActionResult(True, self._conquer_message(action, source.name, target.name))

    def _apply_move(
        self,
        action: MoveAction,
        player_id: int,
    ) -> ActionResult:
        if not can_move(
            self.state,
            player_id,
            action.source_name,
            action.target_name,
            action.count,
        ):
            return ActionResult(False, "Illegal move action.")
        
        # proceed with move
        source = self.state.territories[action.source_name]
        target = self.state.territories[action.target_name]

        source.armies -= action.count
        target.armies += action.count

        self._advance_turn()

        return ActionResult(True, self._move_message(action, source, target))

    def _apply_end_phase(self) -> ActionResult:
        if len(get_territories_owned_by(self.state, self.state.current_player_id)) == 0:
            self._advance_turn()
            return ActionResult(True, "Player Defeated, skipped.")
        if self.state.current_phase == Phase.REINFORCE:
            return ActionResult(False, "You must place all reinforcements.")
        self._advance_turn()
        return ActionResult(True, "Turn ended.")

    def _advance_turn(self):
        self.state.current_player_id = self._next_player_id()
        self.state.current_phase = Phase.REINFORCE
        self.state.turn_number += 1
        self.state.reinforcements_remaining = calculate_reinforcements(
            self.state,
            self.state.current_player_id,
        )

    def _next_player_id(self) -> int:
        player_ids = [player.player_id for player in self.state.players]
        index = player_ids.index(self.state.current_player_id)
        return player_ids[(index + 1) % len(player_ids)]

    def _place_message(self, action: PlaceArmiesAction) -> str:
        return f"Placed {action.count} armies on {action.territory_name}."

    def _conquer_message(self, action: ConquerAction, source_name, target_name) -> str:
        return (
            f"Conquered {target_name} from {source_name}, moved {action.count}"
        )
    
    def _win_message(self, action: AttackAction, source, target) -> str:
        return (
            f"Won against {action.target_name} from {action.source_name}, now {source.armies} against {target.armies}"
        )
    
    def _lose_message(self, action: AttackAction, source, target) -> str:
        return (
            f"Lost against {action.target_name} from {action.source_name}, now {source.armies} against {target.armies}"
        )
    
    def _move_message(self, action: MoveAction, source, target) -> str:
        return (
            f"Moved {action.count} armies from {action.source_name} to {action.target_name}, {source.armies} and {target.armies}"
        )

    def has_valid_attack(self) -> bool:
        player_id = self.state.current_player_id
        return len(get_valid_attacks(self.state, player_id)) > 0
