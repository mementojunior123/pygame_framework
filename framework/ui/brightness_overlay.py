import pygame
from .ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect
from .ui_sprite import UiSprite
from .ui_frame import UiFrame

class BrightnessOverlay(UiSprite):
    def __init__(self, info : BaseDrawableInfo, size : pygame.typing.IntPoint, brightness : int, experimental_blend : bool = True):
        self._experimental_blend : bool = experimental_blend
        self._size : pygame.Vector2 = pygame.Vector2(size)
        self._brightness : int = brightness
        self._render_base(init=True)

        super().__init__(info, self.base_surf)
        self._render()

    @property
    def size(self) -> pygame.Vector2:
        return self._size

    @size.setter
    def size(self, new_value : pygame.typing.IntPoint):
        converted = pygame.Vector2(new_value)
        if converted == self._size:
            return
        self._size = converted
        self._render_base()

    @property
    def brightness(self) -> int:
        return self._brightness

    @brightness.setter
    def brightness(self, new_value : int):
        if new_value == self._brightness:
            return
        self._brightness = new_value
        self._render_base()

    @property
    def experimental_blend(self) -> bool:
        return self._experimental_blend

    def _render_base(self, init : bool = False):
        if self._experimental_blend:
            self._blend_mode = pygame.BLEND_RGB_ADD if self._brightness >= 0 else pygame.BLEND_RGB_MULT
            abs_brightness = abs(self._brightness) if self._brightness >= 0 else 255 - abs(self._brightness)
        else:
            self._blend_mode = pygame.BLEND_RGB_ADD if self._brightness >= 0 else pygame.BLEND_RGB_SUB
            abs_brightness = abs(self._brightness)

        self.base_surf = pygame.surface.Surface(self.size)
        self.base_surf.fill((abs_brightness, abs_brightness, abs_brightness))
        if not init:
            self._render()

    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        draw_rect : pygame.Rect|None = override_draw_pos or (self.get_local_draw_rect() if frame is None else self.get_world_draw_rect(frame))
        if draw_rect is None:
            return
        display.blit(self.surf, draw_rect, special_flags=self._blend_mode)
    