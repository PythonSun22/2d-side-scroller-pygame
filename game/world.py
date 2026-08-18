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
from game.boss import Boss
from game.boss_tuning import BossTuning


class World:
    """
    Owns and coordinates everything inside Freddy's playable world.

    World contains gameplay objects and systems. It does not know about the
    application state manager, menus, options screens, or state transitions.
    """

    PLAYER_START_POSITION = (300, 375)
    GROUND_COLLISION_Y = 476

    BOSS_ARENA_WIDTH = 1500
    BOSS_ARENA_GLOW_WIDTH = 70

    def __init__(
        self,
        screen_size: tuple[int, int],
    ) -> None:
        self.screen_width, self.screen_height = screen_size

        self.background = WorldBackground(screen_size)

        self.world_width = self.background.world_width

        self.boss_arena_left = max(
            0,
            self.world_width - self.BOSS_ARENA_WIDTH,
        )

        self.boss_arena_right = float(self.world_width)
        self.boss_arena_approach = False
        self.boss_arena_locked = False

        self.boss = Boss(
            position=(
                self.boss_arena_right - 180,
                self.GROUND_COLLISION_Y,
            ),
            arena_left=self.boss_arena_left,
            arena_right=self.boss_arena_right,
        )



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
        arena_x = self.boss_arena_left

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
            # Boss arena: low-left
            Platform(
                pygame.Rect(
                    round(arena_x + 140),
                    365,
                    230,
                    24,
                )
            ),

            # Boss arena: long middle platform
            Platform(
                pygame.Rect(
                    round(arena_x + 470),
                    285,
                    610,
                    24,
                )
            ),

            # Boss arena: high-right
            Platform(
                pygame.Rect(
                    round(arena_x + 1120),
                    205,
                    220,
                    24,
                )
            ),
        ]

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.show_debug = not self.show_debug

            if event.key == pygame.K_F2:
                self._debug_teleport_to_boss()

        if self.player.is_transforming or self.player.is_dying:
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

        self.boss.begin_physics_step()

        if not self.fire_powerup.collected:
            self.fire_powerup.begin_physics_step()

        for fireball in self.fireballs:
            fireball.begin_physics_step()

        # ---------------------------------------------------------
        # PLAYER DEATH FREEZE
        # ---------------------------------------------------------

        if self.player.is_dying:
            self.sword.force_sheathed()
            self.player.update_death(delta_time)
            return

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

        self._update_boss_arena()

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
        # Boss
        # ---------------------------------------------------------
        
        self.boss.update(
            delta_time,
            self.player,
            self.platforms,
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
        self._handle_sword_boss_combat()
        self._handle_mob_contact()
        self._handle_fireball_combat()
        self._handle_fireball_boss_combat()
        self._handle_boss_contact()

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

        self.boss.render(
            screen,
            camera_x,
            alpha,
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

        if self.boss.is_active and not self.boss.is_defeated:
            boss_health = self.debug_font.render(
                f"Boss: {self.boss.health}/{BossTuning.MAX_HEALTH}",
                True,
                (255, 90, 90),
            )

            screen.blit(
                boss_health,
                (20, 85),
            )

        self._render_boss_arena_glow(screen)

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

        self.boss.render_debug_hitbox(
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
                f"Boss State: {self.boss.state_name}"
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

    def _update_boss_arena(self) -> None:
        # Freddy has entered the approach to the boss arena.
        if (
            not self.boss_arena_approach
            and self.player.feet_x >= self.boss_arena_left
        ):
            self.boss_arena_approach = True

        # During the approach, allow the normal camera system to keep
        # scrolling until it naturally lines up with the arena.
        if (
            self.boss_arena_approach
            and not self.boss_arena_locked
        ):
            target_camera_x = self.boss_arena_left

            if self.camera.x >= target_camera_x - 1.0:
                self._lock_boss_arena()

        if self.boss_arena_locked:
            self._keep_player_inside_boss_arena()

    def _lock_boss_arena(self) -> None:
        self.boss_arena_locked = True

        self.camera.lock_to(
            self.boss_arena_left
        )

        self.boss.activate()

    def _keep_player_inside_boss_arena(self) -> None:
        if self.player.collision_rect.left >= self.boss_arena_left:
            return

        correction = (
            self.boss_arena_left
            - self.player.collision_rect.left
        )

        self.player.feet_x += correction

        # Refresh Freddy's authoritative rectangles after correcting him.
        self.player.move_horizontal_correction(correction)

    def _render_boss_arena_glow(
        self,
        screen: pygame.Surface,
    ) -> None:
        if not self.boss_arena_locked:
            return

        glow_width = self.BOSS_ARENA_GLOW_WIDTH

        overlay = pygame.Surface(
            (
                self.screen_width,
                self.screen_height,
            ),
            pygame.SRCALPHA,
        )

        for offset in range(glow_width):
            progress = offset / glow_width

            alpha = int(
                65 * (1.0 - progress)
            )

            color = (
                170,
                20,
                25,
                alpha,
            )

            # Left edge
            pygame.draw.line(
                overlay,
                color,
                (offset, offset),
                (
                    offset,
                    self.screen_height - offset,
                ),
            )

            # Right edge
            pygame.draw.line(
                overlay,
                color,
                (
                    self.screen_width - 1 - offset,
                    offset,
                ),
                (
                    self.screen_width - 1 - offset,
                    self.screen_height - offset,
                ),
            )

            # Top edge
            pygame.draw.line(
                overlay,
                color,
                (offset, offset),
                (
                    self.screen_width - offset,
                    offset,
                ),
            )

            # Bottom edge
            pygame.draw.line(
                overlay,
                color,
                (
                    offset,
                    self.screen_height - 1 - offset,
                ),
                (
                    self.screen_width - offset,
                    self.screen_height - 1 - offset,
                ),
            )

        screen.blit(
            overlay,
            (0, 0),
        )

    def _handle_boss_contact(self) -> None:
        if (
            not self.boss.is_active
            or self.boss.is_defeated
        ):
            return

        if self.player.collision_rect.colliderect(
            self.boss.collision_rect
        ):
            self.player.take_damage(
                amount=BossTuning.CONTACT_DAMAGE,
                source_x=self.boss.feet_x,
            )

    def _handle_sword_boss_combat(self) -> None:
        if self.boss.is_defeated:
            return

        sword_hitbox = self.sword.get_attack_hitbox(
            self.player
        )

        if sword_hitbox is None:
            return

        if not self.sword.can_hit(self.boss):
            return

        if not sword_hitbox.colliderect(
            self.boss.collision_rect
        ):
            return

        if self.boss.receive_sword_hit(
            amount=self.sword.current_damage,
            direction=self.sword.knockback_direction,
        ):
            self.sword.register_hit(
                self.boss
            )

    def _handle_fireball_boss_combat(self) -> None:
        if self.boss.is_defeated:
            return

        for fireball in self.fireballs:
            if not fireball.is_active:
                continue

            if not fireball.collision_rect.colliderect(
                self.boss.collision_rect
            ):
                continue

            if self.boss.receive_fireball_hit(
                amount=Fireball.DAMAGE,
            ):
                fireball.start_explosion()

            break

    def _debug_teleport_to_boss(self) -> None:
        target_x = self.boss_arena_left + 180

        correction = (
            target_x
            - self.player.feet_x
        )

        self.player.move_horizontal_correction(
            correction
        )

        # Keep interpolation from drawing Freddy between
        # the old location and the boss arena.
        self.player.previous_feet_x = (
            self.player.feet_x
        )

        self.player.previous_feet_y = (
            self.player.feet_y
        )

        # Let the normal arena-approach logic take over.
        self.boss_arena_approach = True

    def receive_sword_hit(
        self,
        amount: int,
        direction: int,
    ) -> bool:
        if not self.take_damage(amount):
            return False

        self.hit_flash_timer = (
            BossTuning.SWORD_HIT_FLASH_DURATION
        )

        self.stagger_timer = (
            BossTuning.SWORD_HIT_STAGGER_DURATION
        )

        self.knockback_velocity_x = (
            direction
            * BossTuning.SWORD_HIT_KNOCKBACK_SPEED
        )

        return True


    def receive_fireball_hit(
        self,
        amount: int,
    ) -> bool:
        if not self.take_damage(amount):
            return False

        self.hit_flash_timer = (
            BossTuning.FIREBALL_HIT_FLASH_DURATION
        )

        return True

    @property
    def player_defeated(self) -> bool:
        return (
            self.player.is_dying
            and self.player.death_elapsed
            >= PlayerTuning.DEATH_DISPLAY_DURATION
        )


    @property
    def boss_defeated(self) -> bool:
        return (
            self.boss.is_defeated
            and self.boss.should_remove
        )