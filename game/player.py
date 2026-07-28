from __future__ import annotations

import pygame

from game.assets import assets


class Player:
    """
    Minimal Level 1 player.

    This first version only loads and renders Freddy's idle sprite.
    Gameplay behavior will be added incrementally.
    """

    IDLE_IMAGE = "greenFreddy01.png"

    def __init__(
        self,
        position: tuple[int, int],
    ) -> None:
        self.image = assets.load_image(
            self.IDLE_IMAGE,
            alpha=True,
        )

        self.rect = self.image.get_rect()

        self.rect.x = position[0]
        self.rect.y = position[1]

    def update(self, delta_time: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(
            self.image,
            self.rect,
        )