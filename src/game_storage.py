from sys import platform as PLATFORM
import json
import os
from typing import Any, TypedDict
from framework.utils.helpers import AnyJson
from framework.core.base_game_storage import BaseGameStorage, MockGameData

if PLATFORM == 'emscripten':
    from platform import window

class GameData(MockGameData):
    high_score : int

class GameStorage(BaseGameStorage):
    """Exemple implementation of BaseGameStorage."""
    def __init__(self) -> None:
        self.high_score : int = 0

    def reset(self):
        self.high_score = 0
    
    def validate_data(self, data : GameData) -> bool:
        if data is None: return False
        if not isinstance(data.get("high_score", None), int):
            return False
        return True

    def _get_data(self) -> GameData:
        return {'high_score' : self.high_score}

    def _load_data(self, data : GameData) -> bool:
        if not self.validate_data(data):
            print('Data is invalid!')
            return False
        self.high_score = data['high_score']
        return True