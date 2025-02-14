import pygame
from utils.ui.ui_sprite import UiSprite
from utils.helpers import rotate_around_pivot_accurate, ColorType
from utils.pivot_2d import Pivot2D
from typing import Literal

class UiSpriteGroup:
    base_name : str = 'Group'
    def __init__(self, *args : tuple[UiSprite], serial : str = ''):
        self.tag : None = None
        self.elements : list[UiSprite] = [arg for arg in args]
        self.name : str = self.base_name + serial
    
    def draw(self, display : pygame.Surface):
        for element in self.elements:
            element.draw(display)
    
    @staticmethod
    def new_group():
        return UiSpriteGroup(serial='')