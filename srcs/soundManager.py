import pygame
import random

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_loaded = False
        self.load_sound("clic", "sounds/clic.ogg")
        self.load_sound("stones", [
            "sounds/stone1.ogg",
            "sounds/stone2.ogg",
            "sounds/stone3.ogg",
            "sounds/stone4.ogg"
        ])

    def load_sound(self, name, paths):
        if isinstance(paths, str):
            paths = [paths]
        self.sounds[name] = [pygame.mixer.Sound(path) for path in paths]

    def play_sound(self, name):
        if name in self.sounds:
            sound = random.choice(self.sounds[name])
            sound.play()
        else:
            print(f"Son '{name}' non chargé.")

    def load_music(self, path):
        pygame.mixer.music.load(path)
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
