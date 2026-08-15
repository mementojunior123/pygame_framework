import pygame
from .ui_position import AnyUiPosition, UiPosition, AnchorStr
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect

from typing import overload

class UiSprite(UiDrawable):
    _base_surf_changeable = True
    def __init__(self, info : BaseDrawableInfo, base_surf : pygame.Surface):
        super().__init__(info)
        self._base_surf : pygame.Surface = base_surf
        self._surf : pygame.Surface
        self._render()

    @property
    def base_surf(self) -> pygame.Surface:
        return self._base_surf

    @base_surf.setter
    def base_surf(self, new_value : pygame.Surface):
        if not self._base_surf_changeable:
            raise AttributeError(f"Base surf of {self} is not changeable.")
        if self._base_surf == new_value:
            return
        self._base_surf = new_value
        self._render()

    @property
    def surf(self) -> pygame.Surface:
        return self._surf

    @property
    def size(self) -> pygame.Vector2:
        return pygame.Vector2(self._base_surf.get_size())
    
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
        self._surf = self._base_surf.copy()


    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        draw_rect : pygame.Rect|None = override_draw_pos or (self.get_local_draw_rect() if frame is None else self.get_world_draw_rect(frame))
        if draw_rect is None:
            return
        display.blit(self._surf, draw_rect)


def local_imports():
    global UiFrame
    from .ui_frame import UiFrame