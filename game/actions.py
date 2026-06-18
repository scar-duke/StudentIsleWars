from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceArmiesAction:
    territory_name: str
    count: int


@dataclass(frozen=True)
class AttackAction:
    source_name: str
    target_name: str


@dataclass(frozen=True)
class ConquerAction:
    count: int


@dataclass(frozen=True)
class MoveAction:
    source_name: str
    target_name: str
    count: int


@dataclass(frozen=True)
class EndPhaseAction:
    pass
