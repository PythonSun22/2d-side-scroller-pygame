from __future__ import annotations


class MobTuning:
    """Central tuning values for the basic ground mob."""

    HITBOX_WIDTH = 42
    HITBOX_HEIGHT = 56

    HITBOX_VERTICAL_OFFSET = 4
    IMAGE_VERTICAL_OFFSET = 18

    PATROL_SPEED = 90.0
    CHASE_SPEED = 145.0
    RETURN_SPEED = 110.0

    DETECTION_RANGE = 260.0
    DISENGAGE_RANGE = 480.0

    ALERT_DURATION = 0.55
    RETURN_TOLERANCE = 4.0

    ANIMATION_INTERVAL = 0.22

    DEBUG_COLOR = (0, 255, 0)

    CHASE_STOP_RANGE = 12.0