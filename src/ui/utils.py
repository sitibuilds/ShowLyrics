from .qt_imports import QWidget, QGraphicsOpacityEffect, QPropertyAnimation, QByteArray


def fadeAnimation(obj, duration, is_fade_in):
    # type: (QWidget, int, bool) -> None
    if not isinstance(duration, int):
        raise TypeError("Duration must be an integer")

    if not isinstance(obj, QWidget):
        raise TypeError("Object must be an instance of a QWidget")

    effect = QGraphicsOpacityEffect(obj)
    fade_out_animation = QPropertyAnimation(effect, QByteArray("opacity"), obj)
    fade_out_animation.setDuration(duration)

    if not is_fade_in:
        fade_out_animation.setStartValue(1)
        fade_out_animation.setEndValue(0)
    else:
        fade_out_animation.setStartValue(0)
        fade_out_animation.setEndValue(1)

    effect.setOpacity(0)
    obj.setGraphicsEffect(effect)
