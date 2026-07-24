import pygame
import random
from framework.core.base_menu import BaseMenu
from framework.ui import UiSprite
from framework.ui import TextSprite
from framework.ui import BaseUiElements
import framework.utils.tween_module as TweenModule
import framework.utils.interpolation as interpolation
from framework.utils.my_timer import Timer
from framework.ui import BrightnessOverlay
from math import floor, ceil
from framework.utils.helpers import ColorType
from typing import Callable

def noop():
    pass

class Menu(BaseMenu):
    """Implementation of the menu class."""
    font_40 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 40)
    font_50 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 50)
    font_60 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 60)
    font_70 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 70)
    font_150 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 150)

    @staticmethod
    def _get_core_object():
        """Function that imports the core object at runtime."""
        global core_object
        from framework.core.core import core_object
        BaseMenu._get_core_object()
    
    def init(self):
        """Initialises a menu object. Must be ran after runtime imports."""
        self._get_core_object()
        window_size = core_object.main_display.get_size()
        centerx = window_size[0] // 2
        centery = window_size[1] // 2
        wx, wy = window_size

        self.stage = 1
        
        self.stage_data : list[dict] = [None, {}, {}]
        self.stages = [None, 
        [BaseUiElements.new_text_sprite('Game Title', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 50)),
        BaseUiElements.new_button('BlueButton', 'Play', 1, 'midbottom', (centerx, window_size[1] - 15), (0.5, 1.4), 
        (Menu.font_40, 'Black', False), name='play_button'),
        BaseUiElements.new_button('BlueButton', 'Test', 1, 'bottomright', (wx - 15, window_size[1] - 15), (0.5, 1.4), 
        (Menu.font_40, 'Black', False), name='test_button')], #stage 1

        [BaseUiElements.new_button('BlueButton', 'Prev', 1, 'bottomleft', (20, window_size[1] - 25), (0.4, 1.0), 
        (Menu.font_40, 'Black', False), name='prev_button'),
        BaseUiElements.new_button('BlueButton', 'Next', 2, 'bottomright', (wx - 20, window_size[1] - 25), (0.4, 1.0), 
        (Menu.font_40, 'Black', False), name='next_button'),
        BaseUiElements.new_button('BlueButton', 'Back', 3, 'topleft', (15, 15), (0.4, 1.0), 
        (Menu.font_40, 'Black', False), name='back_button'),]
        ]
        self.bg_color = (94, 129, 162)
        self.add_connections()   
    
    def update(self, delta : float):
        """
        Function that runs every frame, allowing frame-based updates to happen.
            delta: The current delta factor. See core.py for more details on delta's functionement.
        """
        super().update(delta)
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                pass
    
    def handle_tag_event(self, event : pygame.Event):
        """
        Event handler for tag events.
            event: The event to handle.
        """
        if event.type != BaseMenu.TAG_EVENT:
            return
        tag : int = event.tag
        name : str = event.name
        trigger_type : str = event.trigger_type
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                if name == "play_button":
                    pygame.event.post(pygame.Event(core_object.START_GAME, {'mode' : 'test'}))
                if name == 'test_button':
                    self.goto_stage(2)
            case 2:
                if name == 'back_button':
                    self.goto_stage(1)
# TODO : Document the menu API (general workflow, interactivity, etc.)