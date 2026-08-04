from __future__ import annotations

import pygame

from game.world_background import WorldBackground
from game.player import Player
from states.base_state import BaseState
from game.platform import Platform
from game.camera import Camera


class WorldState(BaseState):
    def __init__(
        self,
        screen: pygame.Surface,
        state_manager,
    ) -> None:
        super().__init__(screen, state_manager)

        self.background = WorldBackground(
            self.screen.get_size()
        )

        self.world_width = self.background.world_width

        self.camera = Camera(
            screen_width=self.screen.get_width(),
            world_width=self.world_width,
        )

        self.player = Player(
            position=(300, 375),
            world_width=self.world_width,
            ground_y=476,
        )

        self.platforms = [
            Platform(
                pygame.Rect(520, 365, 180, 24)
            ),
            Platform(
                pygame.Rect(820, 295, 180, 24)
            ),
            Platform(
                pygame.Rect(1120, 225, 180, 24)
            ),

            # Additional platforms farther into the world for camera testing.
            Platform(
                pygame.Rect(1600, 355, 200, 24)
            ),
            Platform(
                pygame.Rect(2000, 285, 180, 24)
            ),
            Platform(
                pygame.Rect(2400, 335, 220, 24)
            ),
        ]

        self.debug_font = pygame.font.Font(None, 28)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        self.player.handle_event(event)

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.state_manager.change_state("menu")

        elif event.key == pygame.K_o:
            self.state_manager.change_state("options")

    def update(self, delta_time: float) -> None:
        self.player.update(
            delta_time,
            self.platforms,
        )

        self.camera.update(
            self.player.collision_rect
        )

    def render(self, screen: pygame.Surface) -> None:
        self.background.render(
            screen,
            self.camera.x,
        )

        for platform in self.platforms:
            platform.render(
                screen,
                self.camera.x,
            )

            platform.render_debug(
                screen,
                self.camera.x,
            )

        self.player.render(
            screen,
            self.camera.x,
        )

        self.player.render_debug_hitbox(
            screen,
            self.camera.x,
        )

        debug_surface = self.debug_font.render(
            (
                f"World X: {round(self.player.feet_x)}  "
                f"Camera X: {round(self.camera.x)}"
            ),
            True,
            (255, 255, 255),
        )

        screen.blit(
            debug_surface,
            (20, 20),
        )