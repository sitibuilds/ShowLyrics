from .qt_imports import QWidget, QLabel, QVBoxLayout
from .generic_view_components import (
    GenericWindowView,
    CustomHorizontalLayout,
    CustomVerticalLayout,
    CustomQWidget,
    ColorPickerTool,
    CustomCheckBox,
    CustomSpinBox,
)


class SettingsView(GenericWindowView):
    def __init__(self, parent) -> None:
        # type: (QWidget | None) -> None

        self.__fontSizeSpinBox = CustomSpinBox(
            None, lambda x: print("FontSize SpinBox", x)
        )
        self.__startupLaunchCheckBox = CustomCheckBox(
            None, lambda x: print("Check box", x)
        )
        self.__colorChooser = ColorPickerTool(None, lambda x: print("color picker", x))

        row1 = SettingsRow(None, "Launch on Startup", self.__startupLaunchCheckBox)
        row2 = SettingsRow(None, "Font Size", self.__fontSizeSpinBox)
        row3 = SettingsRow(None, "Background Color", self.__colorChooser)

        super().__init__(parent, "Settings", "", row1, row2, row3)


class SettingsRow(CustomHorizontalLayout):
    def __init__(self, parent, description, widget):
        # type: (QWidget | None, str, QWidget) -> None
        super().__init__(parent, QLabel(description, None), widget)
