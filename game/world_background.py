from __future__ import annotations

import pygame

from game.assets import assets


class WorldBackground:
    """
    Renders the layered World background and ground.

    Scrolling is intentionally disabled for this milestone.
    """

    BACKGROUND_FILES = (
        "world/backgrounds/plx-1.png",
        "world/backgrounds/plx-2.png",
        "world/backgrounds/plx-3.png",
        "world/backgrounds/plx-4.png",
        "world/backgrounds/plx-5.png",
    )

    GROUND_FILE = "world/backgrounds/ground.png"

    def __init__(self, screen_size: tuple[int, int]) -> None:
        self.screen_width, self.screen_height = screen_size

        self.layers = [
            self._load_background_layer(filename)
            for filename in self.BACKGROUND_FILES
        ]

        self.ground = assets.load_image(
            self.GROUND_FILE,
            alpha=True,
        )

        self.ground_y = (
            self.screen_height
            - self.ground.get_height()
        )

    def _load_background_layer(
        self,
        filename: str,
    ) -> pygame.Surface:
        image = assets.load_image(
            filename,
            alpha=True,
        )

        return pygame.transform.smoothscale(
            image,
            (self.screen_width, self.screen_height),
        )

    def render(self, screen: pygame.Surface) -> None:
        for layer in self.layers:
            screen.blit(layer, (0, 0))

        screen.blit(
            self.ground,
            (0, self.ground_y),
        )