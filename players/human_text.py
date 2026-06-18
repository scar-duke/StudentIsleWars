from __future__ import annotations

from game.actions import AttackAction, ConquerAction, MoveAction, EndPhaseAction, PlaceArmiesAction
from game.models import GameState, Phase
from game.rules import get_territories_owned_by, get_valid_attacks, get_valid_moves
from players.base import PlayerController
from ui.text_controller import ask_for_integer, ask_for_option


class HumanTextPlayer(PlayerController):
    def choose_action(self, state: GameState):
        # if we have no territories, we have been defeated, and will skip our turn
        if len(get_territories_owned_by(state, self.player_id)) == 0:
            return EndPhaseAction()

        if state.current_phase == Phase.REINFORCE:
            return self._choose_reinforcement(state)
        return self._act(state)

    def _choose_reinforcement(self, state: GameState) -> PlaceArmiesAction:
        owned = self._owned_territory_names(state)
        print(f"You have {state.reinforcements_remaining} armies to place.")
        territory = ask_for_option("Choose a territory", owned)
        count = ask_for_integer(
            "How many armies?",
            1,
            state.reinforcements_remaining,
        )
        return PlaceArmiesAction(territory, count)

    def _act(self, state: GameState):
        # if we conquered last loop, select the number of armies to move
        if state.current_phase == Phase.CONQUER:
            ###
            count = ask_for_integer(
            "How many armies?",
            1,
            state.last_attack_source.armies-1,
            )
            return ConquerAction(count)

        # choose an option from attack, move, or pass
        options = ["Attack", "Move", "Pass"]
        choice = ask_for_option("Choose an option", options)

        # If attacking, get valid attacks to choose from
        if choice == "Attack":
            attacks = get_valid_attacks(state, self.player_id)
            if len(attacks) == 0:
                print("You have no valid attacks.")
                return
            options.clear()
            options = self._format_options(attacks)
            options.append("Back")
            choice = ask_for_option("Choose an option", options)
            if choice == "Back":
                return
            source, target = self._parse_choice(choice)
            return AttackAction(source, target)
        if choice == "Move":
            moves = get_valid_moves(state, self.player_id)
            if len(moves) == 0:
                print("You have no valid moves.")
                return
            options.clear()
            options = self._format_options(moves)
            options.append("Back")
            choice = ask_for_option("Choose an option", options)
            if choice == "Back":
                return
            source, target = self._parse_choice(choice)

            # Get number of armies to move
            count = ask_for_integer(
            "How many armies to move?",
            0,
            state.territories[source].armies-1,
            )

            return MoveAction(source, target, count)
        if choice == "Pass":
            return EndPhaseAction()
        return

    def _owned_territory_names(self, state: GameState) -> list[str]:
        owned = []
        for name, territory in state.territories.items():
            if territory.owner_id == self.player_id:
                owned.append(name)
        return owned

    def _format_options(
        self,
        items: list[tuple[str, str]],
    ) -> list[str]:
        options = []
        for source, target in items:
            options.append(f"{source} -> {target}")
        return options

    def _parse_choice(self, choice: str) -> tuple[str, str]:
        parts = choice.split(" -> ")
        return parts[0], parts[1]
