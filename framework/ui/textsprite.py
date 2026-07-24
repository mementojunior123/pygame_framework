import pygame
from .ui_position import AnyUiPosition, UiPosition, AnchorStr
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect
from .ui_sprite import UiSprite
from .ui_frame import UiFrame

from framework.utils.helpers import vector_xmax_ysum
from math import floor
from dataclasses import dataclass

@dataclass
class TextSpriteInfo:
    text : str
    font : pygame.Font
    text_color : pygame.typing.ColorLike
    anti_aliasing : bool
    text_stroke_color : pygame.typing.ColorLike|None = None
    text_stroke_size : int|None = None
    max_line_length : int = 0
    newline_height : int = 5
    colorkey : pygame.typing.ColorLike|None = None
    text_percent : float = 1

    def __post_init__(self):
        ...
    

class TextSprite(UiSprite):
    def __init__(self, info : BaseDrawableInfo, text_sprite_info : TextSpriteInfo):
        self._text : str = text_sprite_info.text
        self._font : pygame.Font = text_sprite_info.font
        self._text_color : pygame.typing.ColorLike = text_sprite_info.text_color
        self._anti_aliasing : bool = text_sprite_info.anti_aliasing
        self._text_stroke_color : pygame.typing.ColorLike|None = text_sprite_info.text_stroke_color
        self._text_stroke_width : int|None = text_sprite_info.text_stroke_size
        self._max_line_length : int = text_sprite_info.max_line_length
        self._newline_height : int = text_sprite_info.newline_height
        self._colorkey : pygame.typing.ColorLike|None = text_sprite_info.colorkey

        self._text_percent : float = text_sprite_info.text_percent

        self._render_base(True)
        super().__init__(info, self.base_surf)
        self._render()

    def get_shown_text(self) -> str:
        text_index = floor(self._text_percent * len(self._text))
        return self._text[:text_index + 1]

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_value : str):
        prev_shown_text : str = self.get_shown_text()
        self._text = new_value
        new_shown_text : str = self.get_shown_text()
        if new_shown_text != prev_shown_text:
            self._render_base()

    @property
    def text_percent(self) -> float:
        return self._text_percent

    @text_percent.setter
    def text_percent(self, new_value : float):
        prev_shown_text : str = self.get_shown_text()
        self._text_percent = new_value
        new_shown_text : str = self.get_shown_text()
        if new_shown_text != prev_shown_text:
            self._render_base()

    def _render_base(self, init : bool = False):
        true_text : str = self.get_shown_text()
        if self._text_stroke_color and self._text_stroke_width:
            stroke_x : int = self._text_stroke_width * 2
            stroke_y : int = self._text_stroke_width * 2 * (true_text.count("\n") + 1)
            final_surf_size = (
            pygame.Vector2(stroke_x, stroke_y) 
            + vector_xmax_ysum([self._font.size(chunk) for chunk in true_text.split("\n")])
            + (1,1)
            )
            if self._colorkey:
                final_surf = pygame.Surface(final_surf_size)
                final_surf.fill(self._colorkey)
            else:
                final_surf = pygame.Surface(final_surf_size, pygame.SRCALPHA)

            first_text_sprite = self._font.render(true_text, self._anti_aliasing, self._text_color, wraplength=self._max_line_length)
            outline = self._font.render(true_text, self._anti_aliasing, self._text_stroke_color, wraplength=self._max_line_length)
            

            
            for ox in range(-1, 2):
                for oy in range(-1, 2):
                    if ox or oy or 1:
                        dx, dy = (ox + 1) * self._text_stroke_width, (oy + 1) * self._text_stroke_width
                        #if ((self._text_stroke_width + final_surf.get_width()) % 2):
                        #    dx += 0 if ox > 0 else 0
                        #if ((self.text_stroke_width + final_surf.get_height()) % 2):
                        #    dy += 0 if oy > 0 else 0
                        final_surf.blit(outline, (dx, dy))


            final_surf.blit(first_text_sprite, (self._text_stroke_width, self._text_stroke_width))            
            self.base_surf = final_surf
            if self._colorkey:
                self.base_surf.set_colorkey(self._colorkey)
        else:
            self.base_surf = self._font.render(true_text, self._anti_aliasing, self._text_color, wraplength=self._max_line_length, bgcolor=self._colorkey)
            if self._colorkey:
                self.base_surf.set_colorkey(self._colorkey)
        if not init:
            self._render()