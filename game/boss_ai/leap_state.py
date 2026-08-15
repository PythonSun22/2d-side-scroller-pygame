from game.boss_ai.boss_state import BossState
from game.boss_tuning import BossTuning


class LeapState(BossState):
    """
    Committed jump toward Freddy's approximate horizontal position.
    """

    def __init__(
        self,
        boss,
        target_x: float,
    ) -> None:
        super().__init__(boss)

        self.target_x = target_x
        self.has_left_ground = False

    def enter(self) -> None:
        boss = self.boss

        boss.is_moving = True

        difference_x = (
            self.target_x
            - boss.feet_x
        )

        if difference_x > 0:
            boss.set_direction(1)
        elif difference_x < 0:
            boss.set_direction(-1)

        boss.velocity_y = (
            -BossTuning.LEAP_VERTICAL_SPEED
        )

        boss.is_on_ground = False

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        boss = self.boss

        difference_x = (
            self.target_x
            - boss.feet_x
        )

        if abs(difference_x) > 10:
            boss.feet_x += (
                boss.direction
                * BossTuning.LEAP_HORIZONTAL_SPEED
                * delta_time
            )

            boss.clamp_to_arena()

        if not boss.is_on_ground:
            self.has_left_ground = True

        if (
            self.has_left_ground
            and boss.is_on_ground
        ):
            from game.boss_ai.recovery_state import (
                RecoveryState,
            )

            boss.change_state(
                RecoveryState(boss)
            )