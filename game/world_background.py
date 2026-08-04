from __future__ import annotations

import math

import pygame

from game.assets import assets


class WorldBackground:
    """
    Renders the parallax background and scrolling ground.

    The camera controls horizontal presentation, while the background remains
    unaware of player behavior and collision logic.
    """

    BACKGROUND_FILES = (
        "world/backgrounds/plx-1.png",
        "world/backgrounds/plx-2.png",
        "world/backgrounds/plx-3.png",
        "world/backgrounds/plx-4.png",
        "world/backgrounds/plx-5.png",
    )

    # Distant layers move less than nearby layers.
    PARALLAX_FACTORS = (
        0.05,
        0.12,
        0.22,
        0.38,
        0.60,
    )

    GROUND_FILE = "world/backgrounds/ground.png"

    def __init__(
        self,
        screen_size: tuple[int, int],
    ) -> None:
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

    @property
    def world_width(self) -> int:
        """
        Use the ground artwork as the width of the playable world.
        """
        return max(
            self.screen_width,
            self.ground.get_width(),
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
            (
                self.screen_width,
                self.screen_height,
            ),
        )

    def render(
        self,
        screen: pygame.Surface,
        camera_x: float,
    ) -> None:
        for layer, factor in zip(
            self.layers,
            self.PARALLAX_FACTORS,
        ):
            self._render_tiled_layer(
                screen,
                layer,
                camera_x * factor,
            )

        screen.blit(
            self.ground,
            (
                -round(camera_x),
                self.ground_y,
            ),
        )

    def _render_tiled_layer(
        self,
        screen: pygame.Surface,
        layer: pygame.Surface,
        offset: float,
    ) -> None:
        """
        Repeat one screen-sized layer horizontally so scrolling never exposes
        an empty gap.
        """
        layer_width = layer.get_width()

        starting_x = -(
            round(offset)
            % layer_width
        )

        tile_count = (
            math.ceil(
                self.screen_width
                / layer_width
            )
            + 1
        )

        for tile_index in range(tile_count):
            screen.blit(
                layer,
                (
                    starting_x
                    + tile_index * layer_width,
                    0,
                ),
            )