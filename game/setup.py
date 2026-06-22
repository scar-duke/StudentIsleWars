from __future__ import annotations

import json
import random

from game.models import GameState, Phase, Player, Territory
from game.rules import calculate_reinforcements


def create_initial_state_from_file(player_ids: dict, filename: str, max_armies: int) -> GameState:
    players = []
    for i in range(len(player_ids)):
        players.append(Player(i, player_ids[i].player_name))
        
    territories = load_territories(len(players), max_armies, filename)

    state = GameState(
        territories=territories,
        continent_assignments=create_dict_territories_in_continent(territories.values()),
        players=players,
        current_player_id=0,
        current_phase=Phase.REINFORCE,
        reinforcements_remaining=0,
        last_attack_source=None,
        last_attack_target=None,
        turn_number=1,
    )
    state.reinforcements_remaining = calculate_reinforcements(state, 0)
    return state


def load_territories(num_players: int, max_armies: int, filename: str) -> dict[str, Territory]:
    with open(filename, "r", encoding="utf-8") as input_file:
        map_data = json.load(input_file)
    territories = {}
    for item in map_data["territories"]:
        territory = Territory(
            name=item["name"],
            owner_id=item["owner_id"],
            continent_id=item["continent_id"],
            armies=item["armies"],
            neighbors=item["neighbors"],
        )
        territories[territory.name] = territory

    num_territories = len(territories) // num_players
    assigns = []
    
    for p in range(0, num_players):
        for i in range(num_territories):
            assigns.append(p)
    if len(assigns) != len(territories):
        while(len(assigns) != len(territories)):
            assigns.append(random.randint(0, num_players-1))
    random.shuffle(assigns)

    # after loading in from json file, assign territories to players and numbers of armies
    for i in range(len(territories)):
        num_armies = random.randint(1, max_armies)
        territories[str(i)].owner_id = assigns[i]
        territories[str(i)].armies = num_armies

    return territories


def create_dict_territories_in_continent(territories: list[Territory]) -> dict[str, list[str]]:
    ret = {}
    for t in territories:
        if t.continent_id not in ret:
            ret[t.continent_id] = []
        ret[t.continent_id].append(t.name)
    return ret