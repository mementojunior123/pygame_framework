import pygame

from typing import Literal, TypeAlias

MAIN_DISPLAY_SIZE : tuple[int, int] = (960, 540)
AnchorStr : TypeAlias = Literal['topleft', 'midtop', 'topright', 'midleft', 'center', 'midright', 'bottomleft', 'midbottom', 'bottomright']
AnchorNameList : list[AnchorStr] = ['topleft', 'midtop', 'topright', 'midleft', 'center', 'midright', 'bottomleft', 'midbottom', 'bottomright']
ANCHOR_DICT : dict[AnchorStr, tuple[float, float]] = {
    'topleft' : (0, 0),
    'midtop' : (0.5, 0),
    'topright' : (1, 0),
    'midleft' : (0, 0.5),
    'center' : (0.5, 0.5),
    'midright' : (1.0, 0.5),
    'bottomleft' : (0, 1),
    'midbottom' : (0.5, 1),
    'bottomright' : (1, 1)
}

class UiPosition:
    def __init__(self, position : pygame.typing.Point, 
                 anchor : pygame.typing.Point|AnchorStr):
        if isinstance(anchor, str):
            anchor = ANCHOR_DICT[anchor]
        self._anchor : pygame.Vector2 = pygame.Vector2(anchor)
        self._position : pygame.Vector2 = pygame.Vector2(position)
    
    @staticmethod
    def from_normal_coords(position : pygame.typing.Point, anchor : pygame.typing.Point|AnchorStr, 
                           frame_size : pygame.typing.IntPoint = MAIN_DISPLAY_SIZE):
        actual_position = (position[0] * frame_size[0], position[1] * frame_size[1])
        return UiPosition(actual_position, anchor)
    
    @property
    def x(self) -> int|float:
        return self._position.x
    
    @x.setter
    def x(self, val : int|float):
        self._position.x = val
    
    @property
    def y(self) -> int|float:
        return self._position.y
    
    @y.setter
    def y(self, val : int|float):
        self._position.y = val
    
    @property
    def value(self):
        return self._position
    
    @value.setter
    def value(self, new_val : pygame.Vector2):
        self._position = new_val
    
    def calculate_anchor(self, size : pygame.typing.IntPoint, anchor : pygame.typing.Point|AnchorStr) -> pygame.Vector2:
        if isinstance(anchor, str):
            anchor = ANCHOR_DICT[anchor]
        anchor_offset = pygame.Vector2(anchor) - self._anchor
        pos_offset = pygame.Vector2(anchor_offset.x * size[0], anchor_offset.y * size[1])
        return self.value + pos_offset


AnyUiPosition : TypeAlias = UiPosition

def local_imports3():
    global UiFrame
    from .ui_frame import UiFrame