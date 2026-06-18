from __future__ import annotations

from game.models import GameState, Phase


MIN_REINFORCEMENTS = 2


def get_territories_owned_by(state: GameState, player_id: int) -> list[str]:
    owned = []
    for name, territory in state.territories.items():
        if territory.owner_id == player_id:
            owned.append(name)
    return owned


def calculate_reinforcements(state: GameState, player_id: int) -> int:
    owned = get_territories_owned_by(state, player_id)

    ## calculate base reinforcements
    reinforcements = max(MIN_REINFORCEMENTS, len(owned) // 3)

    ## calculate if a continent bonus is awarded
    for continent in state.continent_assignments.values():
        own_all = True
        for country in continent:
            if country not in owned:
                own_all = False
                break
        if own_all:
            # award extras based on size of continent
            ## if continent size is 5 or less, award continent_size-1
            continent_size = len(continent)
            if continent_size <= 5:
                reinforcements += max(2, continent_size-1)
            ## if continent size is greater than 5, award continent_size-2
            else:
                reinforcements += continent_size-2

    return reinforcements


def is_valid_territory(state: GameState, territory_name: str) -> bool:
    return territory_name in state.territories


def can_place_armies(
    state: GameState,
    player_id: int,
    territory_name: str,
    count: int,
) -> bool:
    if state.current_phase != Phase.REINFORCE:
        return False
    if count <= 0 or count > state.reinforcements_remaining:
        return False
    if not is_valid_territory(state, territory_name):
        return False
    territory = state.territories[territory_name]
    return territory.owner_id == player_id


def are_neighbors(state: GameState, source_name: str, target_name: str) -> bool:
    if not is_valid_territory(state, source_name):
        return False
    source = state.territories[source_name]
    return target_name in source.neighbors


def can_attack(
    state: GameState,
    player_id: int,
    source_name: str,
    target_name: str,
) -> bool:
    if state.current_phase != Phase.CHOOSE:
        return False
    if not is_valid_territory(state, source_name):
        return False
    if not is_valid_territory(state, target_name):
        return False
    source = state.territories[source_name]
    target = state.territories[target_name]
    if source.owner_id != player_id:
        return False
    if target.owner_id == player_id:
        return False
    if not are_neighbors(state, source_name, target_name):
        return False
    # Cannot attack if the source has less than the target
    if source.armies < target.armies:
        return False
    # Cannot attack if the source is only 1 army
    if source.armies == 1:
        return False
    return source.armies >= target.armies


def get_valid_attacks(state: GameState, player_id: int) -> list[tuple[str, str]]:
    attacks = []
    for source_name, source in state.territories.items():
        if source.owner_id != player_id or source.armies <= 1:
            continue
        for target_name in source.neighbors:
            target = state.territories[target_name]
            if target.owner_id != player_id and target.armies <= source.armies:
                attacks.append((source_name, target_name))
    return attacks


def get_valid_moves(state: GameState, player_id: int) -> list[tuple[str, str]]:
    moves = []
    for source_name, source in state.territories.items():
        if source.owner_id != player_id or source.armies <= 1:
            continue
        for target_name in source.neighbors:
            target = state.territories[target_name]
            if target.owner_id == player_id:
                moves.append((source_name, target_name))
    return moves

def can_move(
    state: GameState,
    player_id: int,
    source_name: str,
    target_name: str,
    count: int,
) -> bool:
    if not (state.current_phase == Phase.CHOOSE or state.current_phase == Phase.CONQUER):
        return False
    if not is_valid_territory(state, source_name):
        return False
    if not is_valid_territory(state, target_name):
        return False
    source = state.territories[source_name]
    target = state.territories[target_name]
    if source.owner_id != player_id:
        return False
    if target.owner_id != player_id:
        return False
    if not are_neighbors(state, source_name, target_name):
        return False
    # if the count is an invalid number (less than 0 or would leave source army-less)
    if (count < 0 and state.current_phase == Phase.ATTACK) or (count < 1 and state.current_phase == Phase.CONQUER) or count >= source.armies:
        return False
    return True

def has_player_won(state: GameState, player_id: int) -> bool:
    for territory in state.territories.values():
        if territory.owner_id != player_id:
            return False
    return True
