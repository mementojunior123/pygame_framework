import pygame
from .ui_position import AnyUiPosition, UiPosition

from typing import Literal, TypeAlias, overload, Iterable
from dataclasses import dataclass
import dataclasses

TransformedRect : TypeAlias = dict[Literal['topleft', 'topright', 'bottomright', 'bottomleft'], pygame.Vector2]

@dataclass
class BaseDrawableInfo:
    position : AnyUiPosition
    parent : "UiSpriteGroup|None" = None
    name : str|None = None
    tag : int = 0
    start_visible : bool = True
    use_abs_pos : bool = False
    zindex : int = 0
    data : dict = dataclasses.field(default_factory=lambda : {})

    relevant_events : Iterable[int] = tuple()
    fire_tag_events : bool = True
    obstructs_cliks : bool = True

    def __post_init__(self):
        ...

class UiDrawable:
    TAG_EVENT : int = pygame.event.custom_type()
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

    @staticmethod
    def get_clicked(drawables : list["UiDrawable"], click_pos : pygame.typing.Point, 
                    do_unpack : bool = False, do_sort : bool = False) -> list["UiDrawable"]:
        if do_unpack:
            drawables = UiDrawable.unpack_drawable_list(drawables)
        elif do_sort:
            drawables.sort(key=lambda d : d.zindex)
        result = []
        for drawable in reversed(drawables):
            if drawable.collidepoint(click_pos):
                result.append(drawable)
                if drawable.obstructs_clicks:
                    break
        return result

    def __init__(self, info : BaseDrawableInfo):
        self.position : AnyUiPosition = info.position
        self.name : str|None = info.name
        self.tag : int = info.tag
        self.visible : bool = info.start_visible
        self.unpack : bool = False
        self._parent : "UiSpriteGroup|None" = info.parent
        self.use_abs_pos : bool = info.use_abs_pos
        self.zindex : int = info.zindex
        self.data : dict = info.data

        self._relevant_custom_events : set[int] = set(info.relevant_events)
        self.do_fire_tag_events : bool = info.fire_tag_events
        self.obstructs_clicks : bool = info.obstructs_cliks

    @property
    def relevant_custom_events(self) -> set[int]:
        return self._relevant_custom_events

    @relevant_custom_events.setter
    def relevant_custom_events(self, new_val : Iterable[int]):
        self._relevant_custom_events = set(new_val)

    @property
    def size(self) -> pygame.Vector2:
        raise NotImplementedError

    @property
    def parent(self) -> "UiSpriteGroup|None":
        return self._parent

    def delete(self):
        if self.parent is None:
            return
        self.parent.remove(self)

    def change_parent_to(self, parent : "UiSpriteGroup"):
        if self.parent:
            self.parent.remove(self)
        parent.add(self)

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

    @overload
    def get_world_draw_rect(self, frame : None = None) -> pygame.Rect: ...
    @overload
    def get_world_draw_rect(self, frame : "UiFrame") -> pygame.Rect|None: ...
    
    def get_world_draw_rect(self, frame : "UiFrame|None" = None) -> pygame.Rect|None:
        """Note : If frame is given and not an ancestor, None is returned.
                If None is passed in as a frame, gets window pos"""
        raise NotImplementedError

    def collidepoint(self, point : pygame.typing.Point):
        return self.get_world_draw_rect().collidepoint(point)
    
    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
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

    def on_click(self, event : pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.do_fire_tag_events:
                pygame.event.post(pygame.Event(UiDrawable.TAG_EVENT, 
                {"tag" : self.tag, "name" : self.name, 'trigger_type' : 'click', 'trigger_event' : event}))

    def handle_custom_event(self, event : pygame.Event):
        ...

class UiSpriteGroup(UiDrawable):
    def __init__(self, base_drawable_info : BaseDrawableInfo, elements : list[UiDrawable]):
        super().__init__(base_drawable_info)
        self.elements : list[UiDrawable] = [element for element in elements]
        for element in self.elements:
            if element.parent != self and element.parent:
                if element in element.parent.elements: element.parent.remove(element)
            element._parent = self

    @property
    def relevant_custom_events(self) -> set[int]:
        sets_to_merge : list[set[int]] = [element.relevant_custom_events for element in self.elements]
        result : set[int] = self._relevant_custom_events
        for set_to_merge in sets_to_merge:
            result |= set_to_merge
        return result
    
    @relevant_custom_events.setter
    def relevant_custom_events(self, new_val : Iterable[int]):
        self._relevant_custom_events = set(new_val)

    @property
    def size(self) -> pygame.Vector2:
        return pygame.Vector2(self.get_local_draw_rect().size)

    @staticmethod
    def does_match(target : UiDrawable, drawable : UiDrawable|None, name : str|None, tag : int|None,
                   match_all : bool) -> bool:
        if drawable is None and name is None and tag is None:
            return False
        if not match_all:
            return target == drawable or target.name == name or target.tag == tag
        else:
            if target != drawable and drawable is not None:
                return False
            elif target.name != name and name is not None:
                return False
            elif target.tag != tag and tag is not None:
                return False
            return True


    def search_children(self, drawable : UiDrawable|None = None, name : str|None = None, tag : int|None = None,
                        match_all : bool = False) -> UiDrawable|None:
        if drawable is None and name is None and tag is None:
            return None
        for child in self.elements:
            if self.does_match(child, drawable, name, tag, match_all):
                return child
        return None

    def search_children_multiple(self, drawable : UiDrawable|None = None, name : str|None = None, tag : int|None = None,
                        match_all : bool = False) -> list[UiDrawable]:
        result : list[UiDrawable] = []
        if drawable is None and name is None and tag is None:
            return result
        for child in self.elements:
            if self.does_match(child, drawable, name, tag, match_all):
                result.append(child)
        return result

    def search_descendants(self, drawable : UiDrawable|None = None, name : str|None = None, tag : int|None = None,
                        match_all : bool = False) -> UiDrawable|None:
        if drawable is None and name is None and tag is None:
            return None
        for child in self.elements:
            if self.does_match(child, drawable, name, tag, match_all):
                return child
            elif isinstance(child, UiSpriteGroup) and (child_result := child.search_descendants(drawable, name, tag, match_all)):
                return child_result
        return None

    def search_descendants_multiple(self, drawable : UiDrawable|None = None, name : str|None = None, tag : int|None = None,
                            match_all : bool = False) -> list[UiDrawable]:
        result : list[UiDrawable] = []
        if drawable is None and name is None and tag is None:
            return result
        for child in self.elements:
            if self.does_match(child, drawable, name, tag, match_all):
                result.append(child)
            if isinstance(child, UiSpriteGroup) and (child_result := child.search_descendants_multiple(drawable, name, tag, match_all)):
                result.extend(child_result)
        return result
    
    
    def get_local_draw_rect(self) -> pygame.Rect:
        if not self.elements:
            return pygame.Rect(0, 0, 0, 0)
        return self.elements[0].get_local_draw_rect().unionall([e.get_local_draw_rect() for e in self.elements if e != self.elements[0]])

    @overload
    def get_world_draw_rect(self, frame : None = None) -> pygame.Rect: ...
    @overload
    def get_world_draw_rect(self, frame : "UiFrame") -> pygame.Rect|None: ...
    def get_world_draw_rect(self, frame : "UiFrame|None" = None) -> pygame.Rect|None:
        if not self.elements:
            return pygame.Rect(0, 0, 0, 0)
        if self.get_frame_ancestors(frame) is None:
            return None
        return self.elements[0].get_world_draw_rect(frame).unionall([e.get_world_draw_rect(frame) for e in self.elements if e != self.elements[0]]) # type: ignore
        
    
    def draw(self, display : pygame.Surface, frame : "UiFrame|None" = None, override_draw_pos : pygame.Rect|None = None):
        if not self.visible:
            return
        for element in self.elements:
            element.draw(display, frame)

    def _render(self):
        for element in self.elements:
            element._render()

    def on_click(self, event : pygame.Event):
        super().on_click(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for element in self.elements:
                if element.collidepoint(event.pos):
                    element.on_click(event)

    def handle_custom_event(self, event : pygame.Event):
        for element in self.elements:
            if event.type in element.relevant_custom_events:
                element.handle_custom_event(event)
    
    def add(self, new_element : UiDrawable):
        if new_element not in self.elements:
            self.elements.append(new_element)
            new_element._parent = self

    def remove(self, element : UiDrawable):
        if element not in self.elements:
            raise ValueError("Element is not a chlid of this sprite group.")
        self.elements.remove(element)
        element._parent = None

    def __contains__(self, item):
        return item in self.elements

    def __getitem__(self, index : int):
        return self.elements[index]

    def __delitem__(self, index : int):
        val = self.elements[index]
        if isinstance(val, list):
            for v in val: self.remove(v)
            return
        self.remove(val)

def local_imports2():
    global UiFrame
    from .ui_frame import UiFrame