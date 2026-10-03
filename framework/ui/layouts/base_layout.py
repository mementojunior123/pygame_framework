import pygame

from framework.ui.ui_frame import BaseUiFrameInfo
from ..ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr
from ..ui_sprite import UiSprite
from ..ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect
from ..ui_frame import UiFrame

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

    def _render(self, local_override : TransformedRect|None = None):
        self.update_layout()
        self._surf = pygame.Surface(UiDrawable.get_draw_rect_from_transformed(local_override).size if local_override else self.size, pygame.SRCALPHA)
        for element in self.elements:
            transformed_elem_rect : TransformedRect = self.curr_layout[element]
            element.draw(self._surf, None, override_pos_local=transformed_elem_rect)
        self._surf = pygame.transform.scale_by(self._surf, self.get_true_scale(local_override))
        self._surf = pygame.transform.rotate(self._surf, self.get_true_angle(local_override))
        a : int|None = self._surf.get_alpha()
        self._surf.set_alpha(round((255 if a is None else a) * self.get_true_opacity()))

    def draw(self, display: pygame.Surface, frame : UiFrame | None = None, 
             override_pos_local: TransformedRect|None = None, override_pos_global : pygame.Rect|None = None):
        if not self.visible:
            return
        
        self.temp_local_tranfs_rect = override_pos_local
        self.elements.sort(key = lambda d : d.zindex)
        if self._do_clip:
            self._render(override_pos_local)
            if self._surf is None: return
            draw_rect : pygame.Rect|None = self.calculate_draw_rect(override_pos_global, override_pos_local, frame)
            if draw_rect is None:
                return
            display.blit(self._surf, draw_rect)
        else:
            self.update_layout()
            for element in self.elements:
                transformed_elem_rect : TransformedRect = self.curr_layout[element]
                element.draw(display, self if frame is None else frame, override_pos_local=transformed_elem_rect)
        self.temp_local_tranfs_rect = None