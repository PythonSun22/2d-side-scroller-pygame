from __future__ import annotations

from pathlib import Path

import pygame


class AssetManager:
    """
    Loads and caches game assets from the project's assets directory.

    All asset paths are resolved relative to this file rather than the
    terminal's current working directory.
    """

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parent.parent
        self.assets_directory = self.project_root / "assets"

        self._images: dict[str, pygame.Surface] = {}
        self._fonts: dict[tuple[str, int], pygame.font.Font] = {}

    def get_path(self, relative_path: str) -> Path:
        """
        Return the absolute path to an asset.

        Raises FileNotFoundError immediately when a requested asset does not
        exist, making bad paths easier to diagnose.
        """
        asset_path = self.assets_directory / relative_path

        if not asset_path.is_file():
            raise FileNotFoundError(
                f"Asset not found: {asset_path}"
            )

        return asset_path

    def load_image(
        self,
        relative_path: str,
        *,
        alpha: bool = True,
    ) -> pygame.Surface:
        """
        Load and cache an image.

        Use alpha=True for images with transparency.
        Use alpha=False for solid backgrounds.
        """
        cache_key = f"{relative_path}|alpha={alpha}"

        if cache_key not in self._images:
            image_path = self.get_path(relative_path)
            image = pygame.image.load(str(image_path))

            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            self._images[cache_key] = image

        return self._images[cache_key]

    def load_font(
        self,
        relative_path: str,
        size: int,
    ) -> pygame.font.Font:
        """Load and cache a font at a particular size."""
        if size <= 0:
            raise ValueError("Font size must be greater than zero.")

        cache_key = (relative_path, size)

        if cache_key not in self._fonts:
            font_path = self.get_path(relative_path)

            self._fonts[cache_key] = pygame.font.Font(
                str(font_path),
                size,
            )

        return self._fonts[cache_key]


assets = AssetManager()