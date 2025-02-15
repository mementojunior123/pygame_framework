import pygame
import random
from utils.ui.ui_sprite import UiSprite
from utils.ui.ui_sprite_group import UiSpriteGroup
from utils.ui.textsprite import TextSprite
from utils.ui.base_ui_elements import BaseUiElements
import utils.tween_module as TweenModule
import utils.interpolation as interpolation
from utils.my_timer import Timer
from utils.ui.brightness_overlay import BrightnessOverlay
from math import floor, ceil
from utils.helpers import ColorType
from typing import Callable

def noop():
    pass

class BaseMenu:
    font_40 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 40)
    font_50 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 50)
    font_60 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 60)
    font_70 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 70)
    font_150 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 150)

    def __init__(self) -> None:
        self.stage : int
        self.stages : list[list[UiSprite|UiSpriteGroup]]
        self.bg_color : ColorType|str
        self.temp : dict[UiSprite|UiSpriteGroup, Timer] = {}
        
    def init(self):
        self.bg_color = (94, 129, 162)
        self.stage = 1
        self.stage_data : list[dict] = [None, {}]
        self.stages = [None, []]
    
    def add_temp(self, element : UiSprite|UiSpriteGroup, time : float|Timer, 
                 override = False, time_source : Callable[[], float]|None = None, time_scale : float = 1):
        if element not in self.temp or override == True:
            timer = time if type(time) == Timer else Timer(time, time_source, time_scale)
            self.temp[element] = timer
    
    def alert_player(self, text : str, alert_speed : float = 1):
        text_sprite = TextSprite(pygame.Vector2(core_object.main_display.get_width() // 2, 90), 'midtop', 0, text, 
                        text_settings=(core_object.menu.font_60, 'White', False), text_stroke_settings=('Black', 2), colorkey=(0,255,0))
        
        text_sprite.rect.bottom = -5
        text_sprite.position = pygame.Vector2(text_sprite.rect.center)
        temp_y = text_sprite.rect.centery
        self.add_temp(text_sprite, 5)
        TInfo = TweenModule.TweenInfo
        goal1 = {'rect.centery' : 50, 'position.y' : 50}
        info1 = TInfo(interpolation.quad_ease_out, 0.3 / alert_speed)
        goal2 = {'rect.centery' : temp_y, 'position.y' : temp_y}
        info2 = TInfo(interpolation.quad_ease_in, 0.4 / alert_speed)
        
        on_screen_time = 1 / alert_speed
        info_wait = TInfo(lambda t : t, on_screen_time)
        goal_wait = {}

        chain = TweenModule.TweenChain(text_sprite, [(info1, goal1), (info_wait, goal_wait), (info2, goal2)], True)
        chain.register()
        chain.play()

    def add_connections(self):
        core_object.event_manager.bind(pygame.MOUSEBUTTONDOWN, self.handle_mouse_event)
        core_object.event_manager.bind(UiSprite.TAG_EVENT, self.handle_tag_event)
    
    def remove_connections(self):
        core_object.event_manager.unbind(pygame.MOUSEBUTTONDOWN, self.handle_mouse_event)
        core_object.event_manager.unbind(UiSprite.TAG_EVENT, self.handle_tag_event)
    
    def __get_core_object(self):
        global core_object
        from core.core import core_object

    def render(self, display : pygame.Surface):
        sprite_list : list[UiSprite] = []
        for sprite in (self.stages[self.stage] + list(self.temp.keys())):
            if isinstance(sprite, UiSpriteGroup):
                sprite_list += sprite.elements
            else:
                sprite_list.append(sprite)
        sprite_list.sort(key = lambda sprite : sprite.zindex)
        for sprite in filter(lambda sprite : sprite.visible, sprite_list):
            sprite.draw(display)
        
    
    def update(self, delta : float):
        to_del = []
        for item in self.temp:
            if self.temp[item].isover(): to_del.append(item)
        for item in to_del:
            self.temp.pop(item)

        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                pass
    
    def prepare_entry(self, stage : int = 1):
        self.add_connections()
        self.stage = stage
    
    def prepare_exit(self):
        self.stage = 0
        self.remove_connections()
        self.temp.clear()
    
    def goto_stage(self, new_stage : int):
        self.exit_stage()
        self.enter_stage(new_stage)

    def enter_stage(self, new_stage : int):
        entry_funcion = getattr(self, f'enter_stage{new_stage}', noop)
        entry_funcion()
        self.stage = new_stage
    
    def exit_stage(self):
        entry_funcion = getattr(self, f'exit_stage{self.stage}', noop)
        entry_funcion()

    def launch_game(self):
        new_event = pygame.event.Event(core_object.START_GAME, {})
        pygame.event.post(new_event)

    def get_sprite(self, stage : int, tag : int) -> UiSprite|None:
        """Returns the 1st sprite with a corresponding tag.
        None is returned if it was not found in the stage."""
        if tag is None or stage is None: return None

        the_list : list[UiSprite|UiSpriteGroup] = self.stages[stage]
        for sprite in the_list:
            if sprite.tag == tag:
                return sprite
        return None
    
    def get_sprite_by_name(self, stage, name) -> UiSprite|UiSpriteGroup|None:
        """Returns the 1st sprite with a corresponding name.
        None is returned if it was not found in the stage."""
        if name is None or stage is None: return None

        the_list = self.stages[stage]
        sprite : UiSprite|UiSpriteGroup
        for sprite in the_list:
            if sprite.name == name:
                return sprite
        return None

    def get_sprite_index(self, stage, name = None, tag = None) -> int|None:
        '''Returns the index of the 1st occurence of sprite with a corresponding name or tag.
        None is returned if the sprite is not found'''
        if name is None and tag is None: return None
        the_list = self.stages[stage]
        sprite : UiSprite|UiSpriteGroup
        for i, sprite in enumerate(the_list):
            if sprite.name == name and name is not None:
                return i
            if sprite.tag == tag and tag is not None:
                return i
        return None
    
    def find_and_replace(self, new_sprite : UiSprite|UiSpriteGroup, stage : int, name : str|None = None, 
                         tag : int|None = None, sprite : UiSprite|UiSpriteGroup|None = None) -> bool:
        found : bool = False
        for index, sprite in enumerate(self.stages[stage]):
            if sprite == new_sprite and sprite is not None:
                found = True
                break
            if sprite.tag == tag and tag is not None:
                found = True
                break
            if sprite.name == name and name is not None:
                found = True
                break
        
        if found:
            self.stages[stage][index] = new_sprite
        else:
            print('Find and replace failed')
        return found
    
    def remove_sprite(self, stage : int, sprite : UiSprite|UiSpriteGroup|None = None, 
                      name : str|None = None, tag : int|None = None) -> None|UiSpriteGroup|UiSpriteGroup:
        if sprite is None and name is None and tag is None: return None
        found : UiSprite|UiSpriteGroup|None = None
        for index, element in enumerate(self.stages[stage]):
            if element is None: continue
            if element == sprite and sprite is not None:
                found = element
                break
            if element.tag == tag and tag is not None:
                found = element
                break
            if element.name == name and name is not None:
                found = element
                break
        
        if found:
            self.stages[stage].remove(found)
        else:
            print('Removal failed')
        return found

    def handle_tag_event(self, event : pygame.Event):
        if event.type != UiSprite.TAG_EVENT:
            return
        tag : int = event.tag
        name : str = event.name
        trigger_type : str = event.trigger_type
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                pass
                   
    
    def handle_mouse_event(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos : tuple = event.pos
            sprite : UiSprite|UiSpriteGroup
            for sprite in self.stages[self.stage]:
                if type(sprite) == UiSprite:
                    if sprite.rect.collidepoint(mouse_pos):
                        sprite.on_click()
                elif type(sprite) == UiSpriteGroup:
                    for real_sprite in sprite.elements:
                        if real_sprite.rect.collidepoint(mouse_pos):
                            real_sprite.on_click()

test_list : list[str] = ['up', 'right', 'showdown', 'critical', 'double-up', 'switch', 'fake-run', 'remontada']
class TestUiGroup(UiSpriteGroup):
    base_name = 'TestGroup'
    def __init__(self, *args : tuple[UiSprite], serial : str = '', center : pygame.Vector2 = pygame.Vector2(480, 270)):
        super().__init__(*args, serial=serial)
        self.center = center
    
    @staticmethod
    def new_group(page : int, sep : int = 4, center = pygame.Vector2(480, 270)) -> 'TestUiGroup':
        start_index : int = sep * page
        end_index : int = sep * (page + 1)
        name_amount : int = len(test_list)
        if start_index >= name_amount:
            raise ValueError('Page does not exist')
        if end_index > name_amount: end_index = name_amount
        name_list : list[str] = test_list[start_index: end_index]
        elements : list[TextSprite] = []
        aligments = [(pygame.Vector2(-200, -200), 'topleft'), (pygame.Vector2(200, -200), 'topright'), 
                     (pygame.Vector2(-200, 200), 'bottomleft'),(pygame.Vector2(200, 200), 'bottomright')]
        for text, aligment in zip(name_list, aligments):
            new_sprite = TextSprite(center + aligment[0], aligment[1], 0, text, None, text_settings=(Menu.font_50, 'White', False),
                                    text_stroke_settings=('Black', 2), colorkey=(0, 255, 0))
            elements.append(new_sprite)
        return TestUiGroup(*elements, serial=f'')

            

class Menu(BaseMenu):
    font_40 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 40)
    font_50 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 50)
    font_60 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 60)
    font_70 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 70)
    font_150 = pygame.font.Font(r'assets/fonts/Pixeltype.ttf', 150)
    
    def init(self):
        window_size = core_object.main_display.get_size()
        centerx = window_size[0] // 2
        centery = window_size[1] // 2
        wx, wy = window_size

        self.stage = 1
        
        self.stage_data : list[dict] = [None, {}, {}]
        self.stages = [None, 
        [BaseUiElements.new_text_sprite('Game Title', (Menu.font_60, 'Black', False), 0, 'midtop', (centerx, 50)),
        BaseUiElements.new_button('BlueButton', 'Play', 1, 'midbottom', (centerx, window_size[1] - 15), (0.5, 1.4), 
        {'name' : 'play_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Test', 1, 'bottomright', (wx - 15, window_size[1] - 15), (0.5, 1.4), 
        {'name' : 'test_button'}, (Menu.font_40, 'Black', False))], #stage 1

        [BaseUiElements.new_button('BlueButton', 'Prev', 1, 'bottomleft', (20, window_size[1] - 25), (0.4, 1.0), 
        {'name' : 'prev_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Next', 2, 'bottomright', (wx - 20, window_size[1] - 25), (0.4, 1.0), 
        {'name' : 'next_button'}, (Menu.font_40, 'Black', False)),
        BaseUiElements.new_button('BlueButton', 'Back', 3, 'topleft', (15, 15), (0.4, 1.0), 
        {'name' : 'back_button'}, (Menu.font_40, 'Black', False)),]
        ]
        self.bg_color = (94, 129, 162)
        self.add_connections()   

    def enter_stage2(self):
        self.stage = 2
        sep : int = 4
        self.stage_data[2]['current_page'] = 0
        self.stage_data[2]['max_pages'] = ceil(len(test_list) / sep)
        self.stages[2].append(TestUiGroup.new_group(0))
    
    def change_page_stage2(self, new_page : int):
        self.stage_data[2]['current_page'] = new_page
        self.find_and_replace(TestUiGroup.new_group(new_page), 2, name='TestGroup')
    
    def increment_page_stage2(self):
        new_page : int = (self.stage_data[2]['current_page'] + 1) % self.stage_data[2]['max_pages']
        self.change_page_stage2(new_page)

    def decrement_page_stage2(self):
        new_page : int = (self.stage_data[2]['current_page'] - 1) % self.stage_data[2]['max_pages']
        self.change_page_stage2(new_page)
    
    def exit_stage2(self):
        self.stage_data[2].clear()
        self.remove_sprite(2, name='TestGroup')
    
    def update(self, delta : float):
        stage_data = self.stage_data[self.stage]
        match self.stage:
            case 1:
                pass
    
    def handle_tag_event(self, event : pygame.Event):
        if event.type != UiSprite.TAG_EVENT:
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
                elif name == 'prev_button':
                    self.decrement_page_stage2()
                elif name == 'next_button':
                    self.increment_page_stage2()