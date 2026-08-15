from game.boss_ai.boss_state import BossState
from game.boss_tuning import BossTuning


class StalkState(BossState):
    """
    Slowly approaches Freddy.

    Once within charge range, the boss stops and telegraphs before
    committing to a horizontal charge.
    """

    def __init__(self, boss) -> None:
        super().__init__(boss)

        self.telegraph_elapsed = 0.0

    def enter(self) -> None:
        self.boss.is_moving = True
        self.telegraph_elapsed = 0.0

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        boss = self.boss

        difference_x = (
            player.feet_x
            - boss.feet_x
        )

        difference_y = (
            boss.feet_y 
            - player.feet_y
        )

        distance_to_player = abs(
            difference_x
        )

        # -----------------------------------------------------
        # STALK
        # -----------------------------------------------------
        if (
            difference_y
            >= BossTuning.LEAP_TRIGGER_HEIGHT
            and boss.is_on_ground
        ):
            from game.boss_ai.leap_state import (
                LeapState,
            )

            boss.change_state(
                LeapState(
                    boss,
                    player.feet_x,
                )
            )

            return

        # -----------------------------------------------------
        # STALK
        # -----------------------------------------------------

        if (
            distance_to_player
            > BossTuning.CHARGE_TRIGGER_DISTANCE
        ):
            self.telegraph_elapsed = 0.0

            boss.is_moving = True
            boss.face_world_x(
                player.feet_x
            )

            boss.feet_x += (
                boss.direction
                * BossTuning.STALK_SPEED
                * delta_time
            )

            boss.clamp_to_arena()

            return

        # -----------------------------------------------------
        # TELEGRAPH
        # -----------------------------------------------------

        boss.is_moving = False
        boss.face_world_x(
            player.feet_x
        )

        self.telegraph_elapsed += delta_time

        if (
            self.telegraph_elapsed
            >= BossTuning.CHARGE_TELEGRAPH_DURATION
        ):
            from game.boss_ai.charge_state import (
                ChargeState,
            )

            charge_direction = (
                1
                if player.feet_x > boss.feet_x
                else -1
            )

            boss.change_state(
                ChargeState(
                    boss,
                    charge_direction,
                )
            )