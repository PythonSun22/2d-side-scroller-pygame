from __future__ import annotations

from game.ai.mob_state import MobState
from game.mob_tuning import MobTuning


class ChaseState(MobState):
    """Move horizontally toward Freddy."""

    def enter(self) -> None:
        self.mob.is_moving = True

    def update(self, delta_time: float, player) -> None:
        mob = self.mob

        distance_to_player = abs(
            player.feet_x - mob.feet_x
        )

        # Freddy escaped the chase range.
        if distance_to_player > MobTuning.DISENGAGE_RANGE:
            from game.ai.return_state import ReturnState

            mob.change_state(ReturnState(mob))
            return

        difference_x = player.feet_x - mob.feet_x

        # If Freddy is almost directly above/below the mob,
        # stop moving but keep the current facing direction.
        if abs(difference_x) <= MobTuning.CHASE_STOP_RANGE:
            mob.is_moving = False
            return

        mob.is_moving = True

        if difference_x > 0:
            mob.set_direction(1)
        else:
            mob.set_direction(-1)

        mob.feet_x += (
            mob.direction
            * MobTuning.CHASE_SPEED
            * delta_time
        )