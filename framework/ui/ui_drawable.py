import pygame
from .ui_position import AnyUiPosition, UiPosition, SpecialUiPosition

from typing import Literal, TypeAlias
from dataclasses import dataclass
import dataclasses

TransformedRect : TypeAlias = dict[Literal['topleft', 'topright', 'bottomright', 'bottomleft'], pygame.Vector2]

@dataclass
class BaseDrawableInfo:
    position : AnyUiPosition
    parent : "UiSpriteGroup|None"
    name : str|None = None
    tag : int|None = None
    start_visible : bool = True
    use_abs_pos : bool = False
    zindex : int = 0
    data : dict = dataclasses.field(default_factory=lambda : {})

    def __post_init__():
        ...

class UiDrawable:
    @staticmethod
    def unpack_drawable_list(drawables : list["UiDrawable"]) -> list["UiDrawable"]:
        result : list[UiDrawable] = []
        for drawable in drawables:
            if drawable.unpack and isinstance(drawable, UiSpriteGroup):
                result.extend(drawable.elements)
            else:
                result.append(drawable)
        result.sort(key=lambda d : d.zindex)
        return result
        

    def __init__(self, info : BaseDrawableInfo):
        self.position : AnyUiPosition = info.position
        self.name : str|None = info.name
        self.tag : int|None = info.tag
        self.visible : bool = info.start_visible
        self.unpack : bool = False
        self.parent : "UiSpriteGroup|None" = info.parent
        self.use_abs_pos : bool = info.use_abs_pos
        self.zindex : int = info.zindex
        self.data : dict = info.data

    @property
    def size(self) -> pygame.Vector2:
        raise NotImplementedError

    def get_frame_parent(self) -> "UiFrame|None":
        current_ancestor : UiSpriteGroup|None = self.parent
        while isinstance(current_ancestor, UiDrawable) and not isinstance(current_ancestor, UiFrame):
            current_ancestor = current_ancestor.parent
        return current_ancestor

    def get_frame_ancestors(self, stop : "UiFrame|None" = None) -> list["UiFrame"]|None:
        """Note : If stop is not in the ancestor list, None is returned instead."""
        current_frame : UiFrame|None = self.get_frame_parent()
        ancestor_list : list[UiFrame] = []
        while current_frame is not None:
            ancestor_list.append(current_frame)
            if current_frame == stop and stop is not None:
                return ancestor_list
            current_frame = current_frame.get_frame_parent()
        if stop is not None and stop not in ancestor_list:
            return None
        return ancestor_list

    
    def get_local_rotoscaled_rect(self) -> TransformedRect:
        raise NotImplementedError

    def get_world_rotoscaled_rect(self, frame : "UiFrame|None" = None) -> TransformedRect|None:
        """Note : If frame is given and not an ancestor, None is returned.
        If None is passed in as a frame, gets window pos"""
        raise NotImplementedError
    
    def get_local_draw_rect(self) -> pygame.Rect:
        raise NotImplementedError
    
    def get_world_draw_rect(self, frame : "UiFrame|None" = None) -> pygame.Rect|None:
        """Note : If frame is given and not an ancestor, None is returned.
                If None is passed in as a frame, gets window pos"""
        raise NotImplementedError
    
    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None):
        """
        When frame is None: draw at local pos
        when frame is not None: convert from local to world pos, then draw
        Note : If the frame passed in is not an ancestor of this item, it will be ignored.

        """
        raise NotImplementedError

    def _render(self):
        pass
    
    def update(self, delta : float):
        pass

    def handle_mouse_event(self, event : pygame.Event):
        pass

    def handle_touch_event(self, event : pygame.Event):
        pass

    def handle_key_event(self, event : pygame.Event):
        pass

class UiSpriteGroup(UiDrawable):
    def __init__(self, base_drawable_info : BaseDrawableInfo, elements : list[UiDrawable]):
        super().__init__(base_drawable_info)
        self.elements : list[UiDrawable] = [element for element in elements]

    @property
    def size(self) -> pygame.Vector2:
        return pygame.Vector2(self.get_local_draw_rect().size)
    
    
    def get_local_draw_rect(self) -> pygame.Rect:
        if not self.elements:
            return pygame.Rect(0, 0, 0, 0)
        return self.elements[0].get_local_draw_rect().unionall([e.get_local_draw_rect() for e in self.elements if e != self.elements[0]])
    
    def get_world_draw_rect(self) -> pygame.Rect:
        if not self.elements:
            return pygame.Rect(0, 0, 0, 0)
        return self.elements[0].get_world_draw_rect().unionall([e.get_world_draw_rect() for e in self.elements if e != self.elements[0]])
        
    
    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None):
        if not self.visible:
            return
        for element in self.elements:
            element.draw(display, frame)

    def _render(self):
        for element in self.elements:
            element._render()
    
    def add(self, new_element : UiDrawable):
        if new_element not in self.elements:
            self.elements.append(new_element)

    def __index__(self, index : int):
        return self.elements[index]

def local_imports2():
    global UiFrame
    from .ui_frame import UiFrame