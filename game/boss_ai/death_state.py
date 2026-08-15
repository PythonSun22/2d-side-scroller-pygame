from game.boss_ai.boss_state import BossState
from game.boss_tuning import BossTuning


class DeathState(BossState):
    def __init__(self, boss) -> None:
        super().__init__(boss)

        self.elapsed = 0.0

    def enter(self) -> None:
        boss = self.boss

        boss.is_moving = False
        boss.is_active = False

        boss.frames = boss.death_frames
        boss.current_frame = 0
        boss.animation_elapsed = 0.0

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        self.elapsed += delta_time

        if (
            self.elapsed
            >= BossTuning.DEATH_DISPLAY_DURATION
        ):
            self.boss.should_remove = True