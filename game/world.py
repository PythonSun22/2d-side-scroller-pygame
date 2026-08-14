from __future__ import annotations

import pygame

from game.camera import Camera
from game.platform import Platform
from game.player import Player
from game.world_background import WorldBackground
from game.mob import Mob
from game.player_tuning import PlayerTuning
from game.weapons.sword import Sword
from game.pickups.fire_powerup import FirePowerUp
from game.weapons.fireball import Fireball


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

        self.fire_powerup = FirePowerUp(
            position = (1750, 445)
        )

        self.fireballs: list[Fireball] = []

    def _create_mobs(self) -> list[Mob]:
        return [
            Mob(
                position=(1350, 
                self.GROUND_COLLISION_Y
            ),
                patrol_left=1250,
                patrol_right=1550,
            ),
             Mob(
            position=(
                1900,
                self.GROUND_COLLISION_Y,
            ),
            patrol_left=1780,
            patrol_right=2050,
            ),
            Mob(
                position=(
                    2350,
                    self.GROUND_COLLISION_Y,
                ),
                patrol_left=2220,
                patrol_right=2500,
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.show_debug = not self.show_debug

        if self.player.is_transforming:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._spawn_fireball()

        self.player.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.sword.handle_mouse_down(
                event.button
            )

        elif event.type == pygame.MOUSEBUTTONUP:
            self.sword.handle_mouse_up(
                event.button
            )
            
    def update(self, delta_time: float) -> None:
        # Preserve interpolation state.
        self.player.begin_physics_step()
        self.camera.begin_physics_step()

        for mob in self.mobs:
            mob.begin_physics_step()

        if not self.fire_powerup.collected:
            self.fire_powerup.begin_physics_step()

        for fireball in self.fireballs:
            fireball.begin_physics_step()

        # ---------------------------------------------------------
        # TRANSFORMATION FREEZE
        # ---------------------------------------------------------

        if self.player.is_transforming:
            self.player.update_fire_transformation(
                delta_time
            )
            return

        # ---------------------------------------------------------
        # PLAYER
        # ---------------------------------------------------------

        self.player.update(
            delta_time,
            self.platforms,
        )

        self.sword.update(delta_time)

        # ---------------------------------------------------------
        # FIRE POWER-UP
        # ---------------------------------------------------------

        if not self.fire_powerup.collected:
            # This MUST run every fixed physics step.
            self.fire_powerup.update(delta_time)

            if self.player.collision_rect.colliderect(
                self.fire_powerup.collision_rect
            ):
                self._collect_fire_powerup()

                # Transformation begins immediately.
                return

        # ---------------------------------------------------------
        # MOBS
        # ---------------------------------------------------------

        for mob in self.mobs:
            mob.update(
                delta_time,
                self.player,
            )

        # ---------------------------------------------------------
        # Fireballs
        # ---------------------------------------------------------

        for fireball in self.fireballs:
            fireball.update(delta_time)

        # ---------------------------------------------------------
        # COMBAT
        # ---------------------------------------------------------

        self._handle_sword_combat()
        self._handle_mob_contact()
        self._handle_fireball_combat()

        self.mobs = [
            mob
            for mob in self.mobs
            if not mob.should_remove
        ]

        self.fireballs = [
            fireball for fireball in self.fireballs
            if (
                not fireball.is_finished
                and -100 <= fireball.x <= self.world_width + 100
            )
        ]
        # ---------------------------------------------------------
        # CAMERA
        # ---------------------------------------------------------

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

        self.fire_powerup.render(
            screen,
            camera_x,
            alpha,
        )

        for mob in self.mobs:
            mob.render(
                screen,
                camera_x,
                alpha,
            )

        self.player.render_fire_transformation_aura(
            screen,
            camera_x,
            alpha,
        )

        if self.player.is_transforming:
            player_x, player_y = (
                self.player.get_interpolated_feet_position(
                    alpha
                )
            )

            player_y += (
                self.player.transform_render_offset_y
            )

            flame_text = self.debug_font.render(
                "Flame On!",
                True,
                (255, 165, 0),
            )

            flame_rect = flame_text.get_rect(
                midleft=(
                    round(
                        player_x
                        - camera_x
                        + 40
                    ),
                    round(
                        player_y
                        - 45
                    ),
                )
            )

            screen.blit(
                flame_text,
                flame_rect,
            )

        for fireball in self.fireballs:
            fireball.render(
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

        for fireball in self.fireballs:
            fireball.render_debug(
                screen,
                camera_x,
            )

        self.player.render_debug_hitbox(
            screen,
            camera_x,
            alpha,
        )

        self.sword.render_debug_hitbox(
            screen,
            self.player,
            camera_x,
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
            if mob.is_defeated:
                continue

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

    def _handle_sword_combat(self) -> None:
        sword_hitbox = self.sword.get_attack_hitbox(
            self.player
        )

        if sword_hitbox is None:
            return

        for mob in self.mobs:
            if mob.is_defeated:
                continue

            if not self.sword.can_hit(mob):
                continue

            if not sword_hitbox.colliderect(
                mob.collision_rect
            ):
                continue

            damage_applied = mob.take_damage(
                amount=self.sword.current_damage,
                knockback_direction=(
                    self.sword.knockback_direction
                ),
                knockback_speed=(
                    self.sword.current_knockback_speed
                ),
            )

            if damage_applied:
                self.sword.register_hit(mob)

    def _collect_fire_powerup(self) -> None:
        self.fire_powerup.collect()

        self.sword.force_sheathed()

        self.player.start_fire_transformation()

    def _spawn_fireball(self) -> None:
        if not self.player.has_fire_power:
            return

        if self.player.facing_right:
            direction = 1
            spawn_x = self.player.feet_x + 30
        else:
            direction = -1
            spawn_x = self.player.feet_x - 30

        spawn_y = self.player.feet_y - 45

        self.fireballs.append(
            Fireball(
                position=(
                    spawn_x,
                    spawn_y,
                ),
                direction=direction,
                ground_y=self.GROUND_COLLISION_Y,
            )
        )

    def _handle_fireball_combat(self) -> None:
        for fireball in self.fireballs:
            if not fireball.is_active:
                continue

            for mob in self.mobs:
                if mob.is_defeated:
                    continue

                if not fireball.collision_rect.colliderect(
                    mob.collision_rect
                ):
                    continue

                damage_applied = mob.take_damage(
                    amount=Fireball.DAMAGE,
                    knockback_direction=(
                        fireball.direction
                    ),
                    knockback_speed=(
                        Fireball.KNOCKBACK_SPEED
                    ),
                )

                if damage_applied:
                    fireball.start_explosion()

                # One projectile can hit only one mob.
                break