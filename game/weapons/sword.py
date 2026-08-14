from __future__ import annotations

from enum import Enum, auto

import pygame

from game.assets import assets

import math


class SwordState(Enum):
    SHEATHED = auto()
    DRAWING = auto()
    CHARGING = auto()
    DOWN_SLASH = auto()
    COMBO_WINDOW = auto()
    UP_SLASH = auto()
    RETURNING = auto()


class AttackSide(Enum):
    LEFT = -1
    RIGHT = 1


class Sword:
    """
    Freddy's magically controlled sword.

    Combat behavior is intentionally separated from damage for now.
    This class currently owns only input state, timing, animation, and
    presentation.
    """

    IMAGE_PATH = "weapons/sword1.png"

    WIDTH = 15
    HEIGHT = 77

    # Timing
    DRAW_DURATION = 0.14
    MAX_CHARGE_DURATION = 1.0

    DOWN_SLASH_DURATION = 0.18
    COMBO_WINDOW_DURATION = 0.24
    UP_SLASH_DURATION = 0.18

    RETURN_DURATION = 0.16

    # Sheathed presentation
    SHEATH_X_OFFSET = -20
    SHEATH_Y_OFFSET = -20

    # Sheathed pose: blade points downward behind Freddy.
    SHEATH_ANGLE_RIGHT = 160
    SHEATH_ANGLE_LEFT = -160

    # Ready / charged position
    READY_X_OFFSET = 50
    READY_Y_OFFSET = -105

    # Charged / ready pose: blade points up and away.
    READY_ANGLE_RIGHT = -35
    READY_ANGLE_LEFT = 35

    # End of downward power stroke.
    DOWN_END_ANGLE_RIGHT = -145
    DOWN_END_ANGLE_LEFT = 145
   

    # Low position at end of downward slash.
    DOWN_END_X_OFFSET = 50
    DOWN_END_Y_OFFSET = -15


    # Combat
    DOWN_HITBOX_WIDTH = 52
    DOWN_HITBOX_HEIGHT = 72

    UP_HITBOX_WIDTH = 48
    UP_HITBOX_HEIGHT = 68

    MIN_DOWN_DAMAGE = 1
    MAX_DOWN_DAMAGE = 3

    UP_DAMAGE = 1

    DOWN_KNOCKBACK_SPEED = 150.0
    UP_KNOCKBACK_SPEED = 460.0

    DEBUG_HITBOX_COLOR = (80, 255, 120)

    def __init__(self) -> None:
        image = assets.load_image(
            self.IMAGE_PATH,
            alpha=True,
        )

        self.base_image = pygame.transform.scale(
            image,
            (self.WIDTH, self.HEIGHT),
        )

        self.state = SwordState.SHEATHED
        self.attack_side = AttackSide.RIGHT

        self.state_elapsed = 0.0
        self.charge_elapsed = 0.0

        # True while the mouse button that began the charge is held.
        self.attack_button_held = False
        self.released_charge_ratio = 0.0

        self._hit_target_ids: set[int] = set()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_mouse_down(self, button: int) -> None:
        side = self._side_from_button(button)

        if side is None:
            return

        if self.state == SwordState.SHEATHED:
            self.attack_side = side
            self.attack_button_held = True
            self._change_state(SwordState.DRAWING)
            return

        if self.state == SwordState.COMBO_WINDOW:
            # For now, require the same side/button used for the power stroke.
            if side == self.attack_side:
                self._change_state(SwordState.UP_SLASH)

    def handle_mouse_up(self, button: int) -> None:
        side = self._side_from_button(button)

        if side is None:
            return

        if side != self.attack_side:
            return

        self.attack_button_held = False

        # Releasing while still drawing should cause the attack as soon as
        # the draw motion finishes.
        if self.state == SwordState.CHARGING:
            self._change_state(SwordState.DOWN_SLASH)

    @staticmethod
    def _side_from_button(button: int) -> AttackSide | None:
        if button == 1:
            return AttackSide.LEFT

        if button == 3:
            return AttackSide.RIGHT

        return None

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _change_state(self, new_state: SwordState) -> None:
        self.state = new_state
        self.state_elapsed = 0.0

        if new_state == SwordState.DRAWING:
            self.charge_elapsed = 0.0

        elif new_state == SwordState.SHEATHED:
            self.charge_elapsed = 0.0
            self.attack_button_held = False

        elif new_state == SwordState.DOWN_SLASH:
            self.released_charge_ratio = self.charge_ratio
            self._hit_target_ids.clear()

        elif new_state == SwordState.UP_SLASH:
            self._hit_target_ids.clear()

    def update(self, delta_time: float) -> None:
        self.state_elapsed += delta_time

        if self.state == SwordState.SHEATHED:
            return

        if self.state == SwordState.DRAWING:
            if self.state_elapsed >= self.DRAW_DURATION:
                if self.attack_button_held:
                    self._change_state(SwordState.CHARGING)
                else:
                    self._change_state(SwordState.DOWN_SLASH)

            return

        if self.state == SwordState.CHARGING:
            self.charge_elapsed = min(
                self.charge_elapsed + delta_time,
                self.MAX_CHARGE_DURATION,
            )

            return

        if self.state == SwordState.DOWN_SLASH:
            if self.state_elapsed >= self.DOWN_SLASH_DURATION:
                self._change_state(SwordState.COMBO_WINDOW)

            return

        if self.state == SwordState.COMBO_WINDOW:
            if self.state_elapsed >= self.COMBO_WINDOW_DURATION:
                self._change_state(SwordState.RETURNING)

            return

        if self.state == SwordState.UP_SLASH:
            if self.state_elapsed >= self.UP_SLASH_DURATION:
                self._change_state(SwordState.RETURNING)

            return

        if self.state == SwordState.RETURNING:
            if self.state_elapsed >= self.RETURN_DURATION:
                self._change_state(SwordState.SHEATHED)

    # ------------------------------------------------------------------
    # Useful combat data for later
    # ------------------------------------------------------------------

    @property
    def charge_ratio(self) -> float:
        return min(
            1.0,
            self.charge_elapsed / self.MAX_CHARGE_DURATION,
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _draw_charge_glow(
        self,
        screen: pygame.Surface,
        sword_image: pygame.Surface,
        sword_rect: pygame.Rect,
    ) -> None:
        if self.state not in (
            SwordState.CHARGING,
            SwordState.DOWN_SLASH,
        ):
            return

        if self.state == SwordState.CHARGING:
            charge = self.charge_ratio
        else:
            charge = self.released_charge_ratio

        # Brighter baseline glow.
        padding = int(10 + 14 * charge)
        alpha = int(80 + 140 * charge)

        # At full charge, pulse the glow size and brightness.
        pulse = 0.0

        if (
            self.state == SwordState.CHARGING
            and charge >= 1.0
        ):
            pulse = (
                0.5
                + 0.5
                * math.sin(self.state_elapsed * 10.0)
            )

            padding += int(8 * pulse)
            alpha = min(
                255,
                alpha + int(35 * pulse),
            )

        glow_surface = pygame.Surface(
            (
                sword_rect.width + padding * 2,
                sword_rect.height + padding * 2,
            ),
            pygame.SRCALPHA,
        )

        glow_image = sword_image.copy()

        glow_image.fill(
            (100, 255, 140, alpha),
            special_flags=pygame.BLEND_RGBA_MULT,
        )

        glow_image = pygame.transform.smoothscale(
            glow_image,
            (
                sword_rect.width + padding,
                sword_rect.height + padding,
            ),
        )

        glow_rect = glow_image.get_rect(
            center=(
                glow_surface.get_width() // 2,
                glow_surface.get_height() // 2,
            )
        )

        glow_surface.blit(
            glow_image,
            glow_rect,
        )

        screen.blit(
            glow_surface,
            (
                sword_rect.centerx
                - glow_surface.get_width() // 2,
                sword_rect.centery
                - glow_surface.get_height() // 2,
            ),
            special_flags=pygame.BLEND_RGBA_ADD,
        )

    def render_behind_player(
        self,
        screen: pygame.Surface,
        player,
        camera_x: float,
        alpha: float,
    ) -> None:
        if self.state in (
            SwordState.DOWN_SLASH,
            SwordState.UP_SLASH,
        ):
            return

        player_x, player_y = (
            player.get_interpolated_feet_position(alpha)
        )

        player_y += (
            player.transform_render_offset_y
        )

        if self.state == SwordState.SHEATHED:
            if player.facing_right:
                side = 1
                angle = self.SHEATH_ANGLE_RIGHT
            else:
                side = -1
                angle = self.SHEATH_ANGLE_LEFT

            sword_x = (
                player_x
                - camera_x
                + self.SHEATH_X_OFFSET * side
            )

            sword_y = (
                player_y
                + self.SHEATH_Y_OFFSET
            )

        else:
            offset_x, offset_y, angle = (
                self._get_active_transform()
            )

            sword_x = (
                player_x
                - camera_x
                + offset_x
            )

            sword_y = (
                player_y
                + offset_y
            )

        self._draw_sword(
            screen,
            sword_x,
            sword_y,
            angle,
        )
            
    def render_active(
        self,
        screen: pygame.Surface,
        player,
        camera_x: float,
        alpha: float,
    ) -> None:
        if self.state not in (
            SwordState.DOWN_SLASH,
            SwordState.UP_SLASH,
        ):
            return

        player_x, player_y = (
            player.get_interpolated_feet_position(alpha)
        )

        player_y += (
            player.transform_render_offset_y
        )

        offset_x, offset_y, angle = (
            self._get_active_transform()
        )

        self._draw_sword(
            screen,
            player_x - camera_x + offset_x,
            player_y + offset_y,
            angle,
        )

    def _get_active_transform(
        self,
    ) -> tuple[float, float, float]:
        side = self._side_multiplier()

        ready_x = self.READY_X_OFFSET * side
        ready_y = self.READY_Y_OFFSET
        ready_angle = self._ready_angle()

        down_x = self.DOWN_END_X_OFFSET * side
        down_y = self.DOWN_END_Y_OFFSET
        down_angle = self._down_angle()

        if self.state == SwordState.DRAWING:
            progress = self._normalized_progress(
                self.DRAW_DURATION
            )

            sheath_x = self.SHEATH_X_OFFSET * side
            sheath_y = self.SHEATH_Y_OFFSET

            sheath_angle = (
                self.SHEATH_ANGLE_RIGHT
                if side > 0
                else self.SHEATH_ANGLE_LEFT
            )

            return (
                self._lerp(sheath_x, ready_x, progress),
                self._lerp(sheath_y, ready_y, progress),
                self._lerp_angle(
                    sheath_angle,
                    ready_angle,
                    progress,
                ),
            )

        if self.state == SwordState.CHARGING:
            return (
                ready_x,
                ready_y,
                ready_angle,
            )

        if self.state == SwordState.DOWN_SLASH:
            progress = self._ease_out(
                self._normalized_progress(
                    self.DOWN_SLASH_DURATION
                )
            )

            return (
                self._lerp(ready_x, down_x, progress),
                self._lerp(ready_y, down_y, progress),
                self._lerp_angle(
                    ready_angle,
                    down_angle,
                    progress,
                ),
            )

        if self.state == SwordState.COMBO_WINDOW:
            return (
                down_x,
                down_y,
                down_angle,
            )

        if self.state == SwordState.UP_SLASH:
            progress = self._ease_out(
                self._normalized_progress(
                    self.UP_SLASH_DURATION
                )
            )

            return (
                self._lerp(down_x, ready_x, progress),
                self._lerp(down_y, ready_y, progress),
                self._lerp_angle(
                    down_angle,
                    ready_angle,
                    progress,
                ),
            )

        if self.state == SwordState.RETURNING:
            progress = self._normalized_progress(
                self.RETURN_DURATION
            )

            sheath_x = self.SHEATH_X_OFFSET * side
            sheath_y = self.SHEATH_Y_OFFSET

            sheath_angle = (
                self.SHEATH_ANGLE_RIGHT
                if side > 0
                else self.SHEATH_ANGLE_LEFT
            )

            return (
                self._lerp(ready_x, sheath_x, progress),
                self._lerp(ready_y, sheath_y, progress),
                self._lerp_angle(
                    ready_angle,
                    sheath_angle,
                    progress,
                ),
            )

        return (
            ready_x,
            ready_y,
            ready_angle,
        )

    def _draw_sword(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        angle: float,
    ) -> None:
        rotated_image = pygame.transform.rotate(
            self.base_image,
            angle,
        )

        rect = rotated_image.get_rect(
            center=(
                round(x),
                round(y),
            )
        )

        self._draw_charge_glow(
            screen,
            rotated_image,
            rect,
        )

        screen.blit(
            rotated_image,
            rect,
        )

    # ------------------------------------------------------------------
    # Math helpers
    # ------------------------------------------------------------------

    def _side_multiplier(self) -> int:
        return self.attack_side.value

    def _ready_angle(self) -> float:
        if self.attack_side == AttackSide.RIGHT:
            return self.READY_ANGLE_RIGHT

        return self.READY_ANGLE_LEFT


    def _down_angle(self) -> float:
        if self.attack_side == AttackSide.RIGHT:
            return self.DOWN_END_ANGLE_RIGHT

        return self.DOWN_END_ANGLE_LEFT
    
    def _normalized_progress(
        self,
        duration: float,
    ) -> float:
        if duration <= 0.0:
            return 1.0

        return min(
            1.0,
            self.state_elapsed / duration,
        )

    @staticmethod
    def _lerp(
        start: float,
        end: float,
        progress: float,
    ) -> float:
        return start + (end - start) * progress

    @staticmethod
    def _lerp_angle(
        start: float,
        end: float,
        progress: float,
    ) -> float:
        return start + (end - start) * progress

    @staticmethod
    def _ease_out(progress: float) -> float:
        """
        Quick initial motion that settles toward the end.

        This should make the magical sword stroke feel more forceful than
        perfectly linear movement.
        """
        return 1.0 - (1.0 - progress) ** 2


    @property
    def is_attack_active(self) -> bool:
        return self.state in (
            SwordState.DOWN_SLASH,
            SwordState.UP_SLASH,
        )


    @property
    def current_damage(self) -> int:
        if self.state == SwordState.DOWN_SLASH:
            damage_range = (
                self.MAX_DOWN_DAMAGE
                - self.MIN_DOWN_DAMAGE
            )

            return (
                self.MIN_DOWN_DAMAGE
                + int(
                    self.released_charge_ratio
                    * damage_range
                )
            )

        if self.state == SwordState.UP_SLASH:
            return self.UP_DAMAGE

        return 0


    @property
    def current_knockback_speed(self) -> float:
        if self.state == SwordState.DOWN_SLASH:
            return self.DOWN_KNOCKBACK_SPEED

        if self.state == SwordState.UP_SLASH:
            return self.UP_KNOCKBACK_SPEED

        return 0.0


    @property
    def knockback_direction(self) -> int:
        return self.attack_side.value

    def get_attack_hitbox(
        self,
        player,
    ) -> pygame.Rect | None:
        if not self.is_attack_active:
            return None

        offset_x, offset_y, _ = (
            self._get_active_transform()
        )

        if self.state == SwordState.DOWN_SLASH:
            width = self.DOWN_HITBOX_WIDTH
            height = self.DOWN_HITBOX_HEIGHT
        else:
            width = self.UP_HITBOX_WIDTH
            height = self.UP_HITBOX_HEIGHT

        hitbox = pygame.Rect(
            0,
            0,
            width,
            height,
        )

        hitbox.center = (
            round(player.feet_x + offset_x),
            round(player.feet_y + offset_y),
        )

        return hitbox

    def can_hit(self, target) -> bool:
        return id(target) not in self._hit_target_ids


    def register_hit(self, target) -> None:
        self._hit_target_ids.add(
            id(target)
        )


    def render_debug_hitbox(
        self,
        screen: pygame.Surface,
        player,
        camera_x: float,
    ) -> None:
        hitbox = self.get_attack_hitbox(
            player
        )

        if hitbox is None:
            return

        debug_rect = hitbox.move(
            -round(camera_x),
            0,
        )

        pygame.draw.rect(
            screen,
            self.DEBUG_HITBOX_COLOR,
            debug_rect,
            width=2,
        )

    def force_sheathed(self) -> None:
        self._change_state(
            SwordState.SHEATHED
        )