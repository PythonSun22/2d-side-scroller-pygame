from __future__ import annotations

from enum import Enum, auto

import pygame

from game.assets import assets


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
    UP_SLASH_DURATION = 0.16

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