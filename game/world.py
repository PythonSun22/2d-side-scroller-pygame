from __future__ import annotations

import pygame

from game.camera import Camera
from game.platform import Platform
from game.player import Player
from game.world_background import WorldBackground
from game.mob import Mob
from game.player_tuning import PlayerTuning
from game.weapons.sword import Sword


class World:
    """
    Owns and coordinates everything inside Freddy's playable world.

    World contains gameplay objects and systems. It does not know about the
    application state manager, menus, options screens, or state transitions.
    """

    PLAYER_START_POSITION = (300, 375)
    GROUND_COLLISION_Y = 476

    def __init__(
        self,
        screen_size: tuple[int, int],
    ) -> None:
        self.screen_width, self.screen_height = screen_size

        self.background = WorldBackground(screen_size)

        self.world_width = self.background.world_width

        self.camera = Camera(
            screen_width=self.screen_width,
            world_width=self.world_width,
        )

        self.player = Player(
            position=self.PLAYER_START_POSITION,
            world_width=self.world_width,
            ground_y=self.GROUND_COLLISION_Y,
        )
        self.sword = Sword()

        self.mobs = self._create_mobs()

        self.platforms = self._create_platforms()

        self.debug_font = pygame.font.Font(None, 28)
        self.show_debug = True

    def _create_mobs(self) -> list[Mob]:
        return [
            Mob(
                position=(1350, self.GROUND_COLLISION_Y),
                patrol_left=1250,
                patrol_right=1550,
            ),
        ]

    def _create_platforms(self) -> list[Platform]:
        """
        Build the world's current platform layout.

        These temporary rectangles can later receive visual platform assets
        without changing their collision geometry.
        """
        return [
            Platform(
                pygame.Rect(520, 365, 180, 24)
            ),
            Platform(
                pygame.Rect(820, 295, 180, 24)
            ),
            Platform(
                pygame.Rect(1120, 225, 180, 24)
            ),
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

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        """
        Forward gameplay-specific events to world objects.
        """
        self.player.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.sword.handle_mouse_down(
                event.button
            )

        elif event.type == pygame.MOUSEBUTTONUP:
            self.sword.handle_mouse_up(
                event.button
            )

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.show_debug = not self.show_debug

    def update(self, delta_time: float) -> None:
        self.player.begin_physics_step()
        self.camera.begin_physics_step()

        for mob in self.mobs:
            mob.begin_physics_step()

        self.player.update(
            delta_time,
            self.platforms,
        )
        self.sword.update(delta_time)

        for mob in self.mobs:
            mob.update(delta_time, self.player)

        self._handle_mob_contact()

        self.camera.update(
            self.player.collision_rect
        )

    def render(
        self,
        screen: pygame.Surface,
        alpha: float,
    ) -> None:
        camera_x = self.camera.get_interpolated_x(alpha)

        self.background.render(
            screen,
            camera_x,
        )

        for platform in self.platforms:
            platform.render(
                screen,
                camera_x,
            )

        for mob in self.mobs:
            mob.render(
                screen,
                camera_x,
                alpha,
            )

        self.sword.render_behind_player(
            screen,
            self.player,
            camera_x,
            alpha,
        )

        self.player.render(
            screen,
            camera_x,
            alpha,
        )

        self.sword.render_active(
            screen,
            self.player,
            camera_x,
            alpha,
        )
                

        self._render_hud(screen)

        if self.show_debug:
            self._render_debug(screen, camera_x, alpha)

    def _render_debug(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:

        for platform in self.platforms:
            platform.render_debug(
                screen,
                camera_x,
            )

        for mob in self.mobs:
            mob.render_debug_hitbox(
                screen,
                camera_x,
                alpha,
            )

        self.player.render_debug_hitbox(
            screen,
            camera_x,
            alpha,
        )

        debug_surface = self.debug_font.render(
            (
                f"World X: {round(self.player.feet_x)}  "
                f"Camera X: {round(camera_x)}  "
                "F1: Toggle Debug"
            ),
            True,
            (255, 255, 255),
        )

        screen.blit(
            debug_surface,
            (20, 20),
        )

    def _handle_mob_contact(self) -> None:
        for mob in self.mobs:
            if self.player.collision_rect.colliderect(
                mob.collision_rect
            ):
                self.player.take_damage(
                    amount=PlayerTuning.CONTACT_DAMAGE,
                    source_x=mob.feet_x,
                )

    def _render_hud(
        self,
        screen: pygame.Surface,
    ) -> None:
        health_surface = self.debug_font.render(
            (
                f"Health: {self.player.health}"
                f"/{PlayerTuning.MAX_HEALTH}"
            ),
            True,
            (255, 255, 255),
        )

        screen.blit(
            health_surface,
            (20, 55),
        )