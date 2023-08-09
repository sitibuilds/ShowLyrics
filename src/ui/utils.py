from .qt_imports import (
    QWidget,
    QGraphicsOpacityEffect,
    QPropertyAnimation,
    QByteArray,
)

class CONSTANTS:
    __slots__ = ()
    QWIDGETSIZE_MAX = (
        1 << 24
    ) - 1  # https://riverbankcomputing.com/pipermail/pyqt/2015-April/035748.html


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


def resetFixedSize(widget):
    # type: (QWidget) -> None

    if isinstance(widget, QWidget):
        widget.setMaximumSize(CONSTANTS.QWIDGETSIZE_MAX, CONSTANTS.QWIDGETSIZE_MAX)
        widget.setMinimumSize(0, 0)
