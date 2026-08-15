import pygame

from .ui_position import AnyUiPosition, UiPosition
from framework.utils.helpers import AnchorStr, ANCHOR_REL_POS_DICT
from .ui_drawable import UiDrawable, UiSpriteGroup, BaseDrawableInfo, TransformedRect
from .ui_sprite import UiSprite
from .ui_frame import UiFrame
from .textstyle import TextStyle, TextStyleProxy

from framework.utils.my_timer import Timer, TimeSource
from framework.utils.helpers import vector_xmax_ysum
from math import floor
from dataclasses import dataclass
import dataclasses

from typing import Sequence, Callable, Iterable, Any

@dataclass
class InputTextboxInfo:
    time_source : TimeSource|None = None
    targettable : bool = True
    blink_rate : float = 2
    cursor_color : pygame.typing.ColorLike|None = None
    empty_text : str = ""
    empty_style : TextStyle|None = None
    on_confirm_callbacks : Iterable[Callable[["InputTextbox"], bool|Any]] = dataclasses.field(default_factory=lambda : [])
    writeable_length : float = 0.8
    writeable_height : float = 0.8

    def __post_init__(self):
        ...

class InputTextbox(UiSprite):
    _base_surf_changeable = False
    def __init__(self, info : BaseDrawableInfo, background : pygame.Surface, text : str, text_style : TextStyle,
                 text_pos : AnchorStr|Sequence[float] = (0.5, 0.5), text_aligment : AnchorStr|Sequence[float] = (0.5, 0.5),
                 input_textbox_info : InputTextboxInfo|None = None):
        if isinstance(text_pos, str):
            text_pos = ANCHOR_REL_POS_DICT[text_pos]
        if isinstance(text_aligment, str):
            text_aligment = ANCHOR_REL_POS_DICT[text_aligment]
        if input_textbox_info is None:
            input_textbox_info = InputTextboxInfo()

        self._background : pygame.Surface = background
        self._text : str = text
        self._text_style : TextStyle = text_style
        self._text_pos : pygame.Vector2 = pygame.Vector2(text_pos)
        self._text_alignment : pygame.Vector2 = pygame.Vector2(text_aligment)

        self._focused : bool = False
        self._targetable : bool = input_textbox_info.targettable

        self._blink_timer : Timer = Timer(-1, input_textbox_info.time_source)
        self.blink_rate : float = input_textbox_info.blink_rate
        self._prev_cursor_visibility : bool = False
        
        self._cursor_color = input_textbox_info.cursor_color or text_style.text_color

        self._prev_value : str = text

        self._empty_text : str = input_textbox_info.empty_text
        self._empty_style : TextStyle = input_textbox_info.empty_style or text_style

        self._confirm_callbacks : list[Callable[["InputTextbox"], bool|Any]] = list(input_textbox_info.on_confirm_callbacks)

        self._writeable_rel_size : pygame.Vector2 = pygame.Vector2(input_textbox_info.writeable_length, input_textbox_info.writeable_height)


        self._render_base(True)
        super().__init__(info, self._base_surf)

    
    @property
    def relevant_custom_events(self) -> set[int]:
        return self._relevant_custom_events.union(set((pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, 
                                                      pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION,
                                                      pygame.TEXTEDITING, pygame.TEXTINPUT)))

    @relevant_custom_events.setter
    def relevant_custom_events(self, new_val : Iterable[int]):
        self._relevant_custom_events = set(new_val)
    
    @property
    def background(self) -> pygame.Surface:
        return self._background

    @background.setter
    def background(self, new_value : pygame.Surface):
        self._background = new_value
        self._render_base()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_value : str):
        prev_shown_text : str = self.get_shown_text()
        self._text = new_value
        if self.get_shown_text() != prev_shown_text:
            self._render_base()

    @property
    def text_style(self) -> TextStyleProxy:
        return TextStyleProxy(self._text_style, self._on_style_change)

    @text_style.setter
    def text_style(self, new_value : TextStyle):
        self._text_style = new_value
        self._render_base()

    def set_time_source(self, new_source : TimeSource):
        self._blink_timer.time_source = new_source
        self._blink_timer.restart()

    def get_shown_text(self) -> str:
        if not self._focused:
            return self._text or self._empty_text
        else:
            return self._text + ("|" if self.do_draw_cursor() else "")

    def get_active_style(self) -> TextStyle:
        if not self._focused:
            return self._text_style if self._text != "" else self._empty_style
        else:
            return self._text_style

    def do_draw_cursor(self) -> bool:
        if not self._focused:
            return False
        if floor(self._blink_timer.get_time() / self._blink_timer.duration) % 2 == 0:
            return True
        return False
    
    def focus(self, time_source : TimeSource|None = None):
        if self._focused:
            return
        self._focused = True
        self._prev_value = self._text
        if time_source is not None: 
            self._blink_timer.time_source = time_source
        self._blink_timer.set_duration(0.5)
        self._render_base()
    
    def unfocus(self):
        if not self._focused:
            return
        self._focused = False
        self._prev_value = self._text
        self._render_base()

    def when_backspace(self):
        if self._text: 
            self.text = self.text[:-1]
    
    def when_enter(self):
        result : bool = self.on_confirm()
        if not result:
            self.unfocus()
    
    def on_confirm(self) -> bool:
        stay_focused : bool = False
        for callback in self._confirm_callbacks:
            if callback(self):
                stay_focused = True
        return stay_focused
    
    def when_text_typed(self, text : str):
        self.text = self._text + text
        self._blink_timer.restart()

    def update(self, delta : float):
        if self.do_draw_cursor() != self._prev_cursor_visibility:
            self._render_base()
            self._prev_cursor_visibility = not self._prev_cursor_visibility

    def on_click(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button not in (1, 2, 3):
                return
            if self.get_world_draw_rect().collidepoint(event.pos) and self._targetable:
                self.focus()

    def handle_custom_event(self, event : pygame.Event):
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            self.handle_mouse_event(event)
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.handle_key_event(event)
        elif event.type in (pygame.TEXTINPUT, pygame.TEXTEDITING):
            self.handle_textinput_event(event)

    def handle_mouse_event(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button not in (1, 2, 3):
                return
            if self.get_world_draw_rect().collidepoint(event.pos):
                pass # this case is handled by the more precise .on_click
            else:
                self.unfocus()

    def handle_key_event(self, event : pygame.Event):
        if not self._focused:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._text = self._prev_value
                self.unfocus()
            elif event.key == pygame.K_BACKSPACE:
                self.when_backspace()
            elif event.key == pygame.K_RETURN:
                self.when_enter()
    
    def handle_textinput_event(self, event : pygame.Event):
        if not self._focused:
            return
        if event.type == pygame.TEXTEDITING:
            pass
        elif event.type == pygame.TEXTINPUT:
            self.when_text_typed(event.text)

    def _on_style_change(self, proxy : TextStyleProxy):
        if proxy._value == self._text_style:
            self._render_base()

    def _render_base(self, init : bool = False):
        self._base_surf = self.background.copy()
        shown_text : str = self.get_shown_text()
        active_style : TextStyle = self.get_active_style()
        text_surf : pygame.Surface = active_style.render_text(shown_text)

        text_size = text_surf.get_size()
        theoretical_cursor_width : int
        if self.do_draw_cursor():
            theoretical_cursor_width = 0
        else:
            theoretical_cursor_width = self._text_style.font.size("|")[0]
        max_text_size = (round(self.background.get_width() * self._writeable_rel_size.x) - theoretical_cursor_width, round(self.background.get_height() * self._writeable_rel_size.y))
        actual_text_size : tuple[int, int] = min(text_size[0], max_text_size[0]), min(text_size[1], max_text_size[1])
        text_drawn_rect : pygame.Rect = pygame.Rect(max(text_size[0] - actual_text_size[0], 0), max(text_size[1] - actual_text_size[1], 0), *actual_text_size)
        text_local_topleft : pygame.Vector2 = UiPosition.from_normal_coords(
            self._text_pos, self._text_alignment, self.background.get_size()).calculate_anchor(text_size, 'topleft')
        text_rect = pygame.Rect(text_local_topleft, text_size)
        self._base_surf.blit(text_surf, text_rect, area=text_drawn_rect)
        if not init:
            self._render()