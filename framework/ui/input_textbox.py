import pygame
from math import floor
from framework.ui.ui_sprite import UiSprite
from framework.utils.helpers import rotate_around_pivot_accurate
from framework.utils.my_timer import Timer, TimeSource

class InputTextbox(UiSprite):
    main_image = pygame.image.load('assets/graphics/button_templates/textbox_green_colorkey.png').convert()
    main_image.set_colorkey((0, 255, 0))
    main_font = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 40)
    def __init__(self, surf: pygame.Surface, rect: pygame.Rect, tag: int, text : str = "", name: str | None = None, keep_og_surf=False, 
                 attributes: dict = None, data: dict = None, forced_og_surf: pygame.Surface = None, zindex: int = 0, 
                 text_settings : tuple[pygame.Font, pygame.Color, bool]|None = None, 
                 text_alingment : tuple[pygame.Vector2, int, int]|None = None, 
                 cursor_color : pygame.Color|None = None):
        
        super().__init__(surf, rect, tag, name, True, attributes, data, forced_og_surf, zindex)
        self.text_settings : tuple[pygame.Font, pygame.Color, bool] = text_settings or (InputTextbox.main_font, 'Black', False)
        self._prev_value : str
        self._text : str = text
        self._prev_value : str = text
        self.text_start_pos : pygame.Vector2
        self.max_line_lentgh : int
        self.newline_height : int
        if text_alingment:
            self.text_start_pos, self.max_line_lentgh, self.newline_height, = text_alingment
        else:
            self.text_start_pos = pygame.Vector2(20, 30)
            self.max_line_lentgh = 600
            self.newline_height = 5
        self.focused : bool = False
        self.focus_timer : Timer = Timer(-1)
        self.cursor_color = cursor_color or self.text_settings[1]
        self.targetable : bool = True

        self.prev_cursor_visibility : bool = False

    
    def do_draw_cursor(self) -> bool:
        if not self.focused:
            return False
        if floor(self.focus_timer.get_time() / self.focus_timer.duration) % 2 == 0:
            return True
        return False
    
    def focus(self, time_source : TimeSource|None = None):
        if self.focused:
            return
        self.focused = True
        self._prev_value = self._text
        if time_source is not None: 
            self.focus_timer.time_source = time_source
        self.focus_timer.set_duration(0.5)
    
    def unfocus(self):
        if not self.focused:
            return
        self.focused = False
        self._prev_value = self._text

    def when_backspace(self):
        if self._text: 
            self.text = self.text[:-1]
    
    def when_enter(self):
        self.on_confirm()
        self.unfocus()
    
    def on_confirm(self):
        ...
    
    def when_text_typed(self, text : str):
        self.text = self._text + text
        self.focus_timer.restart()
        print(self.text)
    
    def handle_mouse_event(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button not in (1, 2, 3):
                return
            if self.rect.collidepoint(event.pos) and self.targetable:
                self.focus()
            else:
                self.unfocus()

    
    def handle_key_event(self, event : pygame.Event):
        if not self.focused:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.text = self._prev_value
                self.unfocus()
            elif event.key == pygame.K_BACKSPACE:
                self.when_backspace()
            elif event.key == pygame.K_RETURN:
                self.when_enter()
    
    def handle_textinput_event(self, event : pygame.Event):
        if not self.focused:
            return
        if event.type == pygame.TEXTEDITING:
            pass
        elif event.type == pygame.TEXTINPUT:
            self.when_text_typed(event.text)
        
    def _render(self):
        if self.og_surf is None:
            self.og_surf = self.surf.copy()
        else:
            self.surf = self.og_surf.copy()
        self._render_text()
        scalex_offset, scaley_offset = self._scale.x - 1, self._scale.y - 1
        if abs(scalex_offset) > 0.001 or abs(scaley_offset) > 0.001:
            self.surf = pygame.transform.scale_by(self.surf, self.scale)
        opacity_offset =  1- self._opacity
        
        if abs(self._angle) > 0.001:
            if not self.use_pivot:
                self.surf, self.rect, self.position = rotate_around_pivot_accurate(self.surf, self.position, self._angle, self.position, pygame.Vector2(0,0))
            else:
                self.surf, self.rect, self._position = self._pivot.rotate_image(self.surf)

        if abs(opacity_offset) > 0.002:
            self.surf.set_alpha(self._opacity * 255)        
        for filter in self.filters:
            filter.apply(self.surf)
    
    def _render_text(self):
        theoretical_cursor_size : tuple[int, int] = self.text_settings[0].size(" |")
        space_width : int = self.text_settings[0].size(" ")[0]
        theoretical_cursor_spacing : tuple[int, int] = - space_width + 2
        text_surf_size : tuple[int, int]
        if self._text == '': 
            text_surf_size = (0, self.text_settings[0].get_height())
        else:
            text_surf = self.text_settings[0].render(self._text, self.text_settings[2], self.text_settings[1])
            text_surf_size = text_surf.get_size()
            target_rect : pygame.Rect
            if text_surf_size[0] + theoretical_cursor_size[0] + theoretical_cursor_spacing > self.max_line_lentgh:
                target_rect = pygame.Rect((text_surf_size[0] + theoretical_cursor_size[0] + theoretical_cursor_spacing) - self.max_line_lentgh, 0, self.max_line_lentgh, text_surf_size[1])
            else:
                target_rect = pygame.Rect(0, 0, *text_surf_size)
            self.surf.blit(text_surf, self.text_start_pos, target_rect)
        
        if self.do_draw_cursor():
            cursor : pygame.Surface = self.text_settings[0].render('|', self.text_settings[2], self.cursor_color)
            space_width : int = self.text_settings[0].size(" ")[0]
            text_right = min(self.text_start_pos[0] + text_surf_size[0] + theoretical_cursor_spacing, self.max_line_lentgh - theoretical_cursor_size[0] - theoretical_cursor_spacing * 4)
            text_bottom_right = (text_right, self.text_start_pos[1] + text_surf_size[1])
            cursor_rect = cursor.get_rect(bottomleft=text_bottom_right)
            self.surf.blit(cursor, cursor_rect)

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, new_val : str):
        if new_val != self._text:
            self._text = new_val
            self._render()
            return
    
    def update(self, delta : float):
        if self.do_draw_cursor() != self.prev_cursor_visibility:
            self._render()
            self.prev_cursor_visibility = not self.prev_cursor_visibility