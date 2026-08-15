from .ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect
from .ui_sprite import UiSprite
from .ui_frame import UiFrame
from .textstyle import TextStyle, TextStyleProxy

from framework.utils.helpers import vector_xmax_ysum
from math import floor
from dataclasses import dataclass


@dataclass
class TextSpriteInfo:
    text : str
    style : TextStyle
    text_percent : float = 1

    def __post_init__(self):
        ...

class TextSprite(UiSprite):
    def __init__(self, info : BaseDrawableInfo, text_sprite_info : TextSpriteInfo):
        self._text : str = text_sprite_info.text
        self._style : TextStyle = text_sprite_info.style
        self._text_percent : float = text_sprite_info.text_percent

        self._render_base(True)
        super().__init__(info, self.base_surf)
        self._render()

    def get_shown_text(self) -> str:
        text_index = floor(self._text_percent * len(self._text))
        return self._text[:text_index + 1]

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_value : str):
        prev_shown_text : str = self.get_shown_text()
        self._text = new_value
        new_shown_text : str = self.get_shown_text()
        if new_shown_text != prev_shown_text:
            self._render_base()

    @property
    def text_percent(self) -> float:
        return self._text_percent

    @text_percent.setter
    def text_percent(self, new_value : float):
        prev_shown_text : str = self.get_shown_text()
        self._text_percent = new_value
        new_shown_text : str = self.get_shown_text()
        if new_shown_text != prev_shown_text:
            self._render_base()

    @property
    def style(self) -> TextStyleProxy:
        return TextStyleProxy(self._style, self._on_style_change)

    @style.setter
    def style(self, new_value : TextStyle):
        self._style = new_value

    def _on_style_change(self, proxy : TextStyleProxy):
        if proxy._value == self._style:
            self._render_base()

    def _render_base(self, init : bool = False):
        true_text : str = self.get_shown_text()
        self.base_surf = self._style.render_text(true_text)
        if not init:
            self._render()