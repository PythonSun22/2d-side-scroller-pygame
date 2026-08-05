from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.mob import Mob
    from game.player import Player


class MobState(ABC):
    """Base class for mob AI behavior states."""

    def __init__(self, mob: Mob) -> None:
        self.mob = mob

    def enter(self) -> None:
        """Called once when this state becomes active."""

    def exit(self) -> None:
        """Called once before this state is replaced."""

    @abstractmethod
    def update(
        self,
        delta_time: float,
        player: Player,
    ) -> None:
        """Advance the state by one fixed physics step."""