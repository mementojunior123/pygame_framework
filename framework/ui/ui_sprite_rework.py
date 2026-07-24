import pygame
from .ui_position import AnyUiPosition, UiPosition, SpecialUiPosition, AnchorStr
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect

class UiSprite(UiDrawable):
    def __init__(self, info : BaseDrawableInfo, base_surf : pygame.Surface):
        super().__init__(info)
        self.base_surf : pygame.Surface = base_surf
        self.surf : pygame.Surface = base_surf.copy()


    @property
    def size(self) -> pygame.Vector2:
        raise self.base_surf.get_size()
    
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
    
    def get_world_draw_rect(self, frame : "UiFrame|None" = None) -> pygame.Rect|None:
        world_trs_rect : TransformedRect|None = self.get_world_rotoscaled_rect(frame)
        if world_trs_rect is None: return None
        min_x = min(val.x for val in world_trs_rect.values())
        max_x = max(val.x for val in world_trs_rect.values())
        min_y = min(val.y for val in world_trs_rect.values())
        max_y = max(val.y for val in world_trs_rect.values())
        return pygame.Rect((round(min_x), round(min_y)), (round(max_x - min_x), round(max_y - min_y)))

    def _render(self):
        ...


    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        draw_rect : pygame.Rect = override_draw_pos or (self.get_local_draw_rect() if frame is None else self.get_world_draw_rect(frame))
        display.blit(self.surf, draw_rect)


def runtime_imports():
    global UiFrame
    from .ui_frame import UiFrame