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
    base_surf : pygame.Surface|None = None

    def __post_init__(self):
        ...

class UiFrame(UiSpriteGroup):
    def __init__(self, base_drawable_info : BaseDrawableInfo, elements : list[UiDrawable], ui_frame_info : BaseUiFrameInfo):
        """Note : size arg is ignored if a base surf is passed in"""
        super().__init__(base_drawable_info, elements)
        self._base_size : pygame.Vector2 = pygame.Vector2(ui_frame_info.size)
        self._base_surf : pygame.Surface|None = ui_frame_info.base_surf
        self._surf : pygame.Surface|None = self._base_surf.copy() if self._base_surf else None

    @property
    def base_surf(self) -> pygame.Surface|None:
        return self._base_surf

    @base_surf.setter
    def base_surf(self, new_value : pygame.Surface|None):
        if self._base_surf == new_value:
            return
        self._base_surf = new_value
        self._render()

    @property
    def surf(self) -> pygame.Surface|None:
        return self._surf

    @property
    def size(self) -> pygame.Vector2:
        if self._base_surf is not None:
            return pygame.Vector2(self._base_surf.get_size())
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

    def _render(self):
        super()._render()
        if not self._base_surf:
            self._surf = None
            return
        true_angle : float = self.get_true_angle()
        true_scale : float = self.get_true_scale()
        true_opacity : float = self.get_true_opacity()
        if true_angle != 0 or true_scale != 1:
            self._surf = pygame.transform.rotozoom(self._base_surf, true_angle, true_scale)
        else:
            self._surf = self._base_surf.copy()
        if true_opacity < 1:
            base_alpha : int|None = self._surf.get_alpha()
            if base_alpha is None:
                base_alpha = 255

            self._surf.set_alpha(round(base_alpha * true_opacity))


    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        draw_rect : pygame.Rect|None = override_draw_pos or (self.get_local_draw_rect() if frame is None else self.get_world_draw_rect(frame))
        if draw_rect is None:
            return
        if self._base_surf and self._surf:
            for element in self.elements:
                element.draw(self._surf, None)
            display.blit(self._surf, draw_rect)
        else:
            for element in self.elements:
                element.draw(display, self)
