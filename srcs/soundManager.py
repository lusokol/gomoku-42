import pygame
import random


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.sounds_volume = 5
        self.music_volume = 5
        self.music_loaded = False
        self.load_sound("clic", "sounds/clic.ogg")
        self.load_sound(
            "stones",
            [
                "sounds/stone1.ogg",
                "sounds/stone2.ogg",
                "sounds/stone3.ogg",
                "sounds/stone4.ogg",
            ],
        )

    def load_sound(self, name, paths):
        if isinstance(paths, str):
            paths = [paths]
        self.sounds[name] = [pygame.mixer.Sound(path) for path in paths]
        self._update_sounds_volume(name)

    def _update_sounds_volume(self, name=None):
        volume = self.sounds_volume / 10
        if name:
            for sound in self.sounds[name]:
                sound.set_volume(volume)
        else:
            for sounds in self.sounds.values():
                for sound in sounds:
                    sound.set_volume(volume)

    def play_sound(self, name):
        if name in self.sounds:
            sound = random.choice(self.sounds[name])
            sound.play()
        else:
            print(f"Son '{name}' non chargé.")

    def load_music(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume / 10)
        self.music_loaded = True

    def play_music(self, loop=True):
        if self.music_loaded:
            pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def music_up(self):
        self.music_volume = min(self.music_volume + 1, 10)
        pygame.mixer.music.set_volume(self.music_volume / 10)

    def music_down(self):
        self.music_volume = max(self.music_volume - 1, 0)
        pygame.mixer.music.set_volume(self.music_volume / 10)

    def sound_up(self):
        self.sounds_volume = min(self.sounds_volume + 1, 10)
        self._update_sounds_volume()

    def sound_down(self):
        self.sounds_volume = max(self.sounds_volume - 1, 0)
        self._update_sounds_volume()
