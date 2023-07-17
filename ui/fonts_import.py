from .qt_imports import QFontDatabase
from . import fonts_rc


class __CUSTOM_FONT_ID:

    __SOURCES = {
        "MONTSERRAT_REGULAR": ":/fonts/Montserrat-Regular.ttf",
        "MONTSERRAT_BOLD": ":/fonts/Montserrat-Bold.ttf",
        "MONTSERRAT_SEMIBOLD": ":/fonts/Montserrat-SemiBold.ttf",
    }

    def retrieve_font_id(self, font_name):
        # type: (str) -> int
        if isinstance(font_name, str):
            font_name = font_name.upper()
            if font_name in self.__SOURCES:
                attr_name = self._construct_attribute_from_name(font_name)
                if hasattr(self, attr_name):
                    return self.__getattribute__(attr_name)
                else:
                    font_id = QFontDatabase.addApplicationFont(
                        self.__SOURCES.get(font_name, "")
                    )
                    if font_id < 0:
                        print(f"Failed to load font '{font_name}'")
                    else:
                        self.__setattr__(attr_name, font_id)
                        return font_id
            else:
                raise ValueError(f"Custom font '{font_name}' has not been defined")
        return -1

    def _construct_attribute_from_name(self, font_name):
        # type: (str) -> str
        return "__" + font_name.strip().lower()


CUSTOM_FONT_ID = __CUSTOM_FONT_ID()
