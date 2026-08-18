from __future__ import annotations

import pygame

from game.assets import assets
from states.base_state import BaseState


class VictoryState(BaseState):
    """Application state shown after the boss defeat sequence completes."""

    BACKGROUND_FILE = "world/win_screen.png"

    def __init__(
        self,
        screen: pygame.Surface,
        state_manager,
    ) -> None:
        super().__init__(screen, state_manager)

        self.background = assets.load_image(
            self.BACKGROUND_FILE,
            alpha=False,
        )

        self.background = pygame.transform.smoothscale(
            self.background,
            self.screen.get_size(),
        )

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_r:
            self.state_manager.change_state("world")
            return

        if event.key in (
            pygame.K_RETURN,
            pygame.K_ESCAPE,
        ):
            self.state_manager.change_state("menu")

    def update(self, delta_time: float) -> None:
        pass

    def render(
        self,
        screen: pygame.Surface,
        alpha: float,
    ) -> None:
        screen.blit(
            self.background,
            (0, 0),
        )
