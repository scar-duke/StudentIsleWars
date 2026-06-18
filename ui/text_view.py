from __future__ import annotations

from game.models import ActionResult, GameState


def print_board(state: GameState):
    print("\n" + "=" * 60)
    print(f"Turn {state.turn_number} | Player {state.current_player_id}")
    print(f"Phase: {state.current_phase.name}")
    print("-" * 60)
    for name in state.territories:
        territory = state.territories[name]
        owner = territory.owner_id
        armies = territory.armies
        neighbors = []
        for item in territory.neighbors:
            neighbors.append(item)
        print(f"{name:12} owner={owner} armies={armies:2} neighbors={neighbors}")
    print("=" * 60)


def print_action_result(result: ActionResult):
    if result.success:
        print(f"OK: {result.message}")
    else:
        print(f"ERROR: {result.message}")


def print_game_over(state: GameState):
    winner = None
    for player in state.players:
        if _owns_all_territories(state, player.player_id):
            winner = player
    if winner is not None:
        print(f"Game over. {winner.name} wins!")
    else:
        print("Game over.")


def _owns_all_territories(state: GameState, player_id: int) -> bool:
    for territory in state.territories.values():
        if territory.owner_id != player_id:
            return False
    return True
