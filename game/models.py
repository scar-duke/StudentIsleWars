from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Phase(Enum):
    REINFORCE = auto()
    CHOOSE = auto()
    CONQUER = auto()


@dataclass
class Territory:
    name: str
    owner_id: int | None
    continent_id: int
    armies: int
    neighbors: list[str]


@dataclass
class Player:
    player_id: int
    name: str


@dataclass
class GameState:
    territories: dict[str, Territory]
    continent_assignments: dict[str, list[str]]
    players: list[Player]
    current_player_id: int
    current_phase: Phase
    reinforcements_remaining: int
    last_attack_source: Territory
    last_attack_target: Territory
    turn_number: int


@dataclass
class ActionResult:
    success: bool
    message: str
