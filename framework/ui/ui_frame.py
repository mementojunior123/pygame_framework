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
    do_clip : bool = False

    def __post_init__(self):
        ...

class UiFrame(UiSpriteGroup):
    def __init__(self, base_drawable_info : BaseDrawableInfo, elements : list[UiDrawable], ui_frame_info : BaseUiFrameInfo):
        """Note : size arg is ignored if a base surf is passed in"""
        super().__init__(base_drawable_info, elements)
        self._base_size : pygame.Vector2 = pygame.Vector2(ui_frame_info.size)
        if base_drawable_info.final_anchor is not None: self.change_anchor(base_drawable_info.final_anchor)
        self.obstructs_clicks = False
        self.temp_local_tranfs_rect : TransformedRect|None = None
        self._do_clip = ui_frame_info.do_clip
        self._surf : pygame.Surface|None = None
        if self._do_clip:
            self._render()

    @property
    def do_clip(self) -> bool:
        return self._do_clip

    @do_clip.setter
    def do_clip(self, value : bool):
        self._do_clip = value
        if value:
            self.unpack = False

    @property
    def size(self) -> pygame.Vector2:
        return self._base_size

    @size.setter
    def size(self, value : pygame.Vector2):
        self._base_size = value
    
    def translate_local_to_world(self, point : pygame.typing.Point) -> pygame.Vector2:
        if self.temp_local_tranfs_rect is None:
            point_v2 : pygame.Vector2 = pygame.Vector2(point)

            point_v2.rotate_ip(-self._angle)
            point_v2 *= self._scale.elementwise()

            local_topleft = self.position.calculate_anchor(self.size * self._scale.elementwise(), 'topleft', -self._angle)
            point_v2 += local_topleft
            return point_v2
        else:
            actual_tranfs_rect : TransformedRect = self.get_local_rotoscaled_rect()
            old_x_axis : pygame.Vector2 = (actual_tranfs_rect['topright'] - actual_tranfs_rect['topleft'])
            old_y_axis : pygame.Vector2 = (actual_tranfs_rect['bottomleft'] - actual_tranfs_rect['topleft'])
            x_axis : pygame.Vector2 = (self.temp_local_tranfs_rect['topright'] - self.temp_local_tranfs_rect['topleft']) / old_x_axis.length()
            y_axis : pygame.Vector2 = (self.temp_local_tranfs_rect['bottomleft'] - self.temp_local_tranfs_rect['topleft']) / old_y_axis.length()
            return point[0] * x_axis + point[1] * y_axis + self.temp_local_tranfs_rect['topleft']

    def translate_local_rect_to_world(self, rect : TransformedRect|pygame.Rect) -> TransformedRect:
        if isinstance(rect, pygame.Rect):
            rect_t : TransformedRect = {'topleft' : pygame.Vector2(rect.topleft), 'topright' : pygame.Vector2(rect.topright), 
                                        'bottomright' : pygame.Vector2(rect.bottomright), 'bottomleft' : pygame.Vector2(rect.bottomleft)}
        else: rect_t = rect
        return {k : self.translate_local_to_world(rect_t[k]) for k in rect_t}

    def get_local_rotoscaled_rect(self) -> TransformedRect:
        return {anchor : self.position.calculate_anchor(self.size * self._scale.elementwise(), anchor, -self._angle) 
                        for anchor in ('topleft', 'topright', 'bottomright', 'bottomleft')}

    def get_world_rotoscaled_rect(self, frame : "UiFrame|None" = None, override_local_rect : TransformedRect|None = None) -> TransformedRect|None:
        ancestors = self.get_frame_ancestors(frame)
        if ancestors is None:
            return None
        current_result : TransformedRect = override_local_rect or self.get_local_rotoscaled_rect()
        for ancestor in ancestors:
            current_result = ancestor.translate_local_rect_to_world(current_result)
        return current_result
        
    def get_local_draw_rect(self) -> pygame.Rect:
        local_trs_rect = self.get_local_rotoscaled_rect()
        return UiDrawable.get_draw_rect_from_transformed(local_trs_rect)

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

    def _render(self, local_override : TransformedRect|None = None):
        self._surf = pygame.Surface(UiDrawable.get_draw_rect_from_transformed(local_override).size if local_override else self.size, pygame.SRCALPHA)
        for element in self.elements:
            element.draw(self._surf, None)
        self._surf = pygame.transform.scale_by(self._surf, self.get_true_scale(local_override))
        self._surf = pygame.transform.rotate(self._surf, self.get_true_angle(local_override))
        a : int|None = self._surf.get_alpha()
        self._surf.set_alpha(round((255 if a is None else a) * self.get_true_opacity()))

    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, 
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
            for element in self.elements:
                element.draw(display, self if frame is None else frame)
        self.temp_local_tranfs_rect = None
