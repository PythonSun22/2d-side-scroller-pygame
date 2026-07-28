from __future__ import annotations

import pygame

from game.level_background import LevelBackground
from game.player import Player
from states.base_state import BaseState


class Level1State(BaseState):
    def __init__(
        self,
        screen: pygame.Surface,
        state_manager,
    ) -> None:
        super().__init__(screen, state_manager)

        self.background = LevelBackground(
            self.screen.get_size()
        )

        self.player = Player(
            position=(300, 375),
        )

        self.debug_font = pygame.font.Font(None, 28)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.state_manager.change_state("menu")

        elif event.key == pygame.K_o:
            self.state_manager.change_state("options")

    def update(self, delta_time: float) -> None:
        self.player.update(delta_time)

    def render(self, screen: pygame.Surface) -> None:
        self.background.render(screen)
        self.player.render(screen)

        debug_surface = self.debug_font.render(
            "Level 1 foundation — movement comes next",
            True,
            (255, 255, 255),
        )

        screen.blit(
            debug_surface,
            (20, 20),
        )