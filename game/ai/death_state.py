from __future__ import annotations

import pygame

from game.ai.mob_state import MobState
from game.mob_tuning import MobTuning


class DeathState(MobState):
    """Display the original death sprite before removing the mob."""

    def __init__(self, mob) -> None:
        super().__init__(mob)

        self.timer = (
            MobTuning.DEATH_DISPLAY_DURATION
        )

    def enter(self) -> None:
        mob = self.mob

        mob.is_moving = False

        image = mob.death_image

        if mob.facing_right:
            image = pygame.transform.flip(
                image,
                True,
                False,
            )

        mob.image = image

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        self.timer -= delta_time

        if self.timer <= 0.0:
            self.mob.should_remove = True