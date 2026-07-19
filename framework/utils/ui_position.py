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
    def __init__(self, position : pygame.Vector2|tuple[float, float], 
                 anchor : tuple[float, float]|pygame.Vector2|AnchorStr,
                 ui_frame : None = None, use_normal_coords : bool = False):
        if isinstance(anchor, str):
            anchor = ANCHOR_DICT[anchor]
        self._anchor : pygame.Vector2 = pygame.Vector2(anchor)
        self._position : pygame.Vector2 = pygame.Vector2(position)
        self._ui_frame : None = ui_frame
        self._use_normal_coords : bool = use_normal_coords
    
    @property
    def x(self) -> int|float:
        return self._position.x
    
    @x.setter
    def x(self, val : int|float):
        self._x = val
    
    @property
    def y(self) -> int|float:
        return self._y
    
    @y.setter
    def y(self, val : int|float):
        self._y = val
    
    @property
    def position(self):
        return self._position
    
    
    
    def calculate_topleft(self, ui_frame : None = None):
        ...
    
    def calculate_center(self, ui_frame : None = None):
        ...
    
    def get_abs_pos(self, ui_frame : None = None):
        ...
    
    def get_pos(self, normalise : bool = False, ui_frame : None = None):
        ...

class SpecialUiPosition:
    def __init__(self, x : int|float, y : int|float):
        self._x : int|float = x
        self._y : int|float = y

    @property
    def x(self) -> int|float:
        return self._x
    
    @x.setter
    def x(self, val : int|float):
        self._x = val
    
    @property
    def y(self) -> int|float:
        return self._y
    
    @y.setter
    def y(self, val : int|float):
        self._y = val
    
    @property
    def position(self) -> pygame.Vector2:
        return pygame.Vector2(self._x, self._y)
    
    @position.setter
    def position(self, new_val : pygame.Vector2|tuple[int, int]):
        self._x = new_val[0]
        self._y = new_val[1]

AnyUiPosition : TypeAlias = UiPosition|SpecialUiPosition