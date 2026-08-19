import pygame
from .ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr
from .ui_sprite import UiSprite
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect

from typing import overload
from dataclasses import dataclass

@dataclass
class BaseUiFrameInfo:
    """Note : size arg is ignored if a base surf is passed in"""
    size : pygame.typing.IntPoint

    def __post_init__(self):
        ...

class UiFrame(UiSpriteGroup):
    def __init__(self, base_drawable_info : BaseDrawableInfo, elements : list[UiDrawable], ui_frame_info : BaseUiFrameInfo):
        """Note : size arg is ignored if a base surf is passed in"""
        super().__init__(base_drawable_info, elements)
        self._base_size : pygame.Vector2 = pygame.Vector2(ui_frame_info.size)
        if base_drawable_info.final_anchor is not None: self.change_anchor(base_drawable_info.final_anchor)

    @property
    def size(self) -> pygame.Vector2:
        return self._base_size

    @size.setter
    def size(self, value : pygame.Vector2):
        self._base_size = value
    
    def translate_local_to_world(self, point : pygame.typing.Point) -> pygame.Vector2:
        point_v2 : pygame.Vector2 = pygame.Vector2(point)

        point_v2.rotate_ip(-self._angle)
        if (mag := point_v2.magnitude()) != 0:
            point_v2.scale_to_length(mag * self._scale)

        local_topleft = self.position.calculate_anchor(self.size * self._scale, 'topleft', -self._angle)
        point_v2 += local_topleft
        return point_v2

    def translate_local_rect_to_world(self, rect : TransformedRect|pygame.Rect) -> TransformedRect:
        if isinstance(rect, pygame.Rect):
            rect_t : TransformedRect = {'topleft' : pygame.Vector2(rect.topleft), 'topright' : pygame.Vector2(rect.topright), 
                                        'bottomright' : pygame.Vector2(rect.bottomright), 'bottomleft' : pygame.Vector2(rect.bottomleft)}
        else: rect_t = rect
        return {k : self.translate_local_to_world(rect_t[k]) for k in rect_t}

    def get_local_rotoscaled_rect(self) -> TransformedRect:
        return {anchor : self.position.calculate_anchor(self.size * self._scale, anchor, -self._angle) 
                        for anchor in ('topleft', 'topright', 'bottomright', 'bottomleft')}

    def get_world_rotoscaled_rect(self, frame : "UiFrame|None" = None) -> TransformedRect|None:
        ancestors = self.get_frame_ancestors(frame)
        if ancestors is None:
            return None
        current_result : TransformedRect = self.get_local_rotoscaled_rect()
        for ancestor in ancestors:
            current_result = ancestor.translate_local_rect_to_world(current_result)
        return current_result
        
    def get_local_draw_rect(self) -> pygame.Rect:
        local_trs_rect = self.get_local_rotoscaled_rect()
        min_x = min(val.x for val in local_trs_rect.values())
        max_x = max(val.x for val in local_trs_rect.values())
        min_y = min(val.y for val in local_trs_rect.values())
        max_y = max(val.y for val in local_trs_rect.values())
        return pygame.Rect((round(min_x), round(min_y)), (round(max_x - min_x), round(max_y - min_y)))

    @overload
    def get_world_draw_rect(self, frame : None = None) -> pygame.Rect: ...
    @overload
    def get_world_draw_rect(self, frame : "UiFrame") -> pygame.Rect|None: ...
    def get_world_draw_rect(self, frame : "UiFrame|None" = None) -> pygame.Rect|None:
        world_trs_rect : TransformedRect|None = self.get_world_rotoscaled_rect(frame)
        if world_trs_rect is None: return None
        min_x = min(val.x for val in world_trs_rect.values())
        max_x = max(val.x for val in world_trs_rect.values())
        min_y = min(val.y for val in world_trs_rect.values())
        max_y = max(val.y for val in world_trs_rect.values())
        return pygame.Rect((round(min_x), round(min_y)), (round(max_x - min_x), round(max_y - min_y)))

    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        draw_rect : pygame.Rect|None = override_draw_pos or (self.get_local_draw_rect() if frame is None else self.get_world_draw_rect(frame))
        if draw_rect is None:
            return
        else:
            for element in self.elements:
                element.draw(display, self)
