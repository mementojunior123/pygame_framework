import pygame
from .ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr
from .ui_sprite import UiSprite
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect

from typing import overload
from dataclasses import dataclass

@dataclass
class BaseUiFrameInfo:
    size : pygame.typing.IntPoint
    base_surf : pygame.Surface|None = None

    def __post_init__(self):
        ...





class UiFrame(UiSpriteGroup):
    def __init__(self, base_drawable_info : BaseDrawableInfo, elements : list[UiDrawable], ui_frame_info : BaseUiFrameInfo):
        super().__init__(base_drawable_info, elements)
        self._size : pygame.Vector2 = pygame.Vector2(ui_frame_info.size)
        self.base_surf : pygame.Surface|None = ui_frame_info.base_surf
        self.surf : pygame.Surface|None = self.base_surf.copy() if self.base_surf else None
        self.unpack = self.base_surf is not None

    @property
    def size(self) -> pygame.Vector2:
        return self._size

    @size.setter
    def size(self, value : pygame.Vector2):
        self._size = value
    

    def translate_local_to_world(self, point : pygame.typing.Point) -> pygame.Vector2:
        point_v2 : pygame.Vector2 = pygame.Vector2(point)

        local_topleft = self.position.calculate_anchor(self.size, 'topleft')
        #TODO : Handle rotation and scale
        point_v2 += local_topleft
        return point_v2

    def translate_local_rect_to_world(self, rect : TransformedRect|pygame.Rect) -> TransformedRect:
        if isinstance(rect, pygame.Rect):
            rect_t : TransformedRect = {'topleft' : pygame.Vector2(rect.topleft), 'topright' : pygame.Vector2(rect.topright), 
                                        'bottomright' : pygame.Vector2(rect.bottomright), 'bottomleft' : pygame.Vector2(rect.bottomleft)}
        else: rect_t = rect
        return {k : self.translate_local_to_world(rect_t[k]) for k in rect_t}

    def get_local_rotoscaled_rect(self) -> TransformedRect:
        return {anchor : self.position.calculate_anchor(self.size, anchor) for anchor in ('topleft', 'topright', 'bottomright', 'bottomleft')}

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

    def _render(self):
        super()._render()
        if not self.surf:
            return
        ...


    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        draw_rect : pygame.Rect|None = override_draw_pos or (self.get_local_draw_rect() if frame is None else self.get_world_draw_rect(frame))
        if draw_rect is None:
            return
        if self.base_surf:
            self.surf = self.base_surf.copy()
            for element in self.elements:
                element.draw(self.surf, None)
            display.blit(self.surf, draw_rect)
        else:
            for element in self.elements:
                element.draw(display, self)
