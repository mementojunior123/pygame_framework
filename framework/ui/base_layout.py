import pygame

from framework.ui.ui_frame import BaseUiFrameInfo
from .ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr
from .ui_sprite import UiSprite
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect
from .ui_frame import UiFrame

from typing import overload, Any
from dataclasses import dataclass

class BaseLayout(UiFrame):
    ...
    # Ability to control de position of its elements
    # Ability to automatically scale its elements?

    def __init__(self, base_drawable_info: BaseDrawableInfo, elements: list[UiDrawable], ui_frame_info: BaseUiFrameInfo):
        super().__init__(base_drawable_info, elements, ui_frame_info)

    def update_layout(self):
        ...

    def _calculate_local_draw_pos(self, element : UiDrawable, element_position_data : Any = None, 
                                  other_data : dict|None = None) -> TransformedRect:
        ...