from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.boss import Boss
    from game.player import Player


class BossState(ABC):
    def __init__(self, boss: Boss) -> None:
        self.boss = boss

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    @abstractmethod
    def update(
        self,
        delta_time: float,
        player: Player,
    ) -> None:
        pass