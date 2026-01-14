import pygame
import json

class SoundTypes:
    music = 'Music'
    sfx = 'SFX'

class WebChannel:
    def __init__(self, path : str, sound_ref : pygame.mixer.Sound|None, channel_id : int, loop_count : int, volume : float,
                  play_now : bool = True):
        self.bg_manager : BgManager = core_object.bg_manager
        self.volume : float = volume
        self._id : int = channel_id
        core_object.run_js_source_file('make_web_channel', {
            "AUDIO_PATH" : path,
            "PLAY_NOW" : str(play_now).lower(),
            "VOLUME" : str(sound_ref.get_volume() * self.bg_manager.global_volume * volume * self.bg_manager.web_mult),
            "CHANNEL_ID" : str(self._id),
            "LOOP_COUNT" : str(loop_count),
        })
    
    @property
    def id(self) -> int:
        return self._id
    
    def pause(self):
        core_object.run_js_source_file('dispatch_event', {
            "EVENT_TYPE" : "PauseAudio",
            "EVENT_ARGS" : json.dumps({'id' : self._id})
        })
    

class BgManager:
    WebChannel = WebChannel
    def __init__(self, core_refrence : "Core") -> None:
        global core_object
        core_object = core_refrence
        self.core : "Core" = core_refrence
        self.current : dict[pygame.mixer.Channel, TrackInfo] = {}
        self.global_volume = 1
        self.web_mult : float = 1.0
        self.sound_types = SoundTypes
        if 'make_web_channel' not in self.core.js_source:
            self.core.load_js_source_file('framework/core/web_audio/web_audio.js', 'make_web_channel', {
                "AUDIO_PATH" : None,
                "PLAY_NOW" : "true",
                "VOLUME" : None,
                "CHANNEL_ID" : None,
                "LOOP_COUNT" : None,
            })
        self.SOUNDS : dict[str, tuple[pygame.mixer.Sound, str]] = {}
        sound_list : list[tuple[str, str, float]] = [
            ('test_music', 'assets/audio/music/test_music.ogg', 1.0),
            ('test_sfx', 'assets/audio/sfx/test_sfx.ogg', 1.0)
        ]
        for name, path, vol in sound_list:
            self.load_sound(path, vol, name)
    
    def load_sound(self, path : str, vol : float, name : str):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(vol)
        self.SOUNDS[name] = (sound, path)
    
    def test_play_web(self, name : str):
        if not self.core.is_web(): return
        sound_ref, path = self.SOUNDS[name]
        WebChannel(path, sound_ref, pygame.mixer.find_channel().id, -1, 0.1)

    def set_global_volume(self, new_volume):
        self.global_volume = new_volume
        for channel in self.current:
            info : TrackInfo = self.current[channel]
            channel.set_volume(self.global_volume * info.volume)

       

    def play(self, track : pygame.mixer.Sound, volume, loops = -1, maxtime = 0, fade_ms = 0, sound_type : str|None = 'Music'):
        """Used for playing music."""
        channel = track.play(loops, maxtime, fade_ms)
        if not channel:
            core_object.log("Attempted to play track, but ran out of audio channels!")
            return
        if volume < 1 or volume > 1:
            channel.set_volume(volume * self.global_volume)
            print('hello world')
        self.current[channel] = TrackInfo(volume, sound_type)
        return channel
    
    def play_sfx(self, sfx : pygame.mixer.Sound, volume, loops = 0, maxtime = 0, fade_ms = 0, sound_type : str|None = 'SFX'):
        """Used for playing short sound effects."""
        if not channel:
            core_object.log("Attempted to play sfx, but ran out of audio channels!")
            return
        channel = sfx.play(loops, maxtime, fade_ms)
        channel.set_volume(volume * self.global_volume)
        self.current[channel] = TrackInfo(volume, sound_type)
        return channel
        
    def get_channels(self, sound : pygame.mixer.Sound) -> list[pygame.mixer.Channel]:
        """Gets all the channels that are playing a specific sound."""
        channels : list[pygame.mixer.Channel] = []
        for channel in self.current:
            if channel.get_sound() == sound:
                channels.append(channel)
        return channels
    
    def get_all_type(self, t : str) -> list[pygame.mixer.Channel]:
        """Get all channels that are playing a sound of a specific type."""
        channels : list[pygame.mixer.Channel] = []
        for channel in self.current:
            info = self.current[channel]
            if info.type == t:
                channels.append(channel)
        
        return channels

    def stop_channel(self, channel : pygame.mixer.Channel):
        """Stop a currently playing channel."""
        channel.stop()
        if channel in self.current:
            self.current.pop(channel)
    
    def stop_sound(self, sound : pygame.mixer.Sound):
        """Stop a currently playing track."""
        to_remove : list[pygame.mixer.Channel] = []
        for channel in self.current:
            if channel.get_sound() == sound:
                to_remove.append(channel)
        
        for channel in to_remove:
            self.current.pop(channel)
        
        sound.stop()
    
    def stop_all_type(self, t : str):
        """Stop all sounds of a specific type."""
        to_remove : list[pygame.mixer.Channel] = []
        for channel in self.current:
            info = self.current[channel]
            if info.type == t:
                to_remove.append(channel)
        
        for channel in to_remove:
            self.stop_channel(channel)
    
    def stop_all_music(self):
        """Stop all sounds of type "Music".
        Equivalent to stop_all_type("Music")."""
        self.stop_all_type(self.sound_types.music)

    def stop_all(self):
        """Stops all currently playing sounds."""
        for channel in self.current:
            channel.stop()
        self.current.clear()
            

    def update(self):
        to_remove : list[pygame.mixer.Channel] = []
        for channel in self.current:
            if not channel.get_busy():
                to_remove.append(channel)
        for channel in to_remove:
            self.current.pop(channel)   


class TrackInfo:
    def __init__(self, volume : float, sound_type : str|None = None) -> None:
        self.volume : float = volume
        self.type : str|None = sound_type



def _runtime_hints():
    global Core
    from framework.core.core import Core