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
        self.curr_layout : dict[UiDrawable, TransformedRect] = {}

    def update_layout(self):
        self.curr_layout = {elem : elem.get_local_rotoscaled_rect() for elem in self.elements}

    def _calculate_local_draw_pos(self, element : UiDrawable, element_position_data : Any = None, 
                                  other_data : dict|None = None) -> TransformedRect:
        ...

    def draw(self, display: pygame.Surface, frame : UiFrame | None = None, 
             override_pos_local: TransformedRect|None = None, override_pos_global : pygame.Rect|None = None):
        if not self.visible:
            return
        self.update_layout()
        self.temp_local_tranfs_rect = override_pos_local
        for element in self.elements: 
            transformed_elem_rect : TransformedRect = self.curr_layout[element]
            element.draw(display, self, override_pos_local=transformed_elem_rect)
        self.temp_local_tranfs_rect = None