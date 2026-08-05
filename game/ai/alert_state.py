from __future__ import annotations

from game.ai.mob_state import MobState
from game.mob_tuning import MobTuning


class AlertState(MobState):
    """
    Brief reaction pause after detecting Freddy.

    The mob faces Freddy before beginning pursuit.
    """

    def __init__(self, mob) -> None:
        super().__init__(mob)
        self.timer = MobTuning.ALERT_DURATION

    def enter(self) -> None:
        self.mob.is_moving = False

    def update(self, delta_time: float, player) -> None:
        mob = self.mob

        mob.face_world_x(player.feet_x)

        distance_to_player = abs(
            player.feet_x - mob.feet_x
        )

        if distance_to_player > MobTuning.DISENGAGE_RANGE:
            from game.ai.return_state import ReturnState

            mob.change_state(ReturnState(mob))
            return

        self.timer -= delta_time

        if self.timer <= 0.0:
            from game.ai.chase_state import ChaseState

            mob.change_state(ChaseState(mob))