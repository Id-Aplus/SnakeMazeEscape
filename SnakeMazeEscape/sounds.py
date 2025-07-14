import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.volume = 0.7
        self.music_volume = 0.3
        
        # Load sounds and start background music
        self.create_sounds()
        self.start_background_music()
    
    def create_sounds(self):
        """Load sound files from Downloads/SFX folder"""
        sound_files = {
            'shoot': 'C:/Users/HP/Downloads/SFX/shoot.wav.wav',        # Space bar shooting
            'victory': 'C:/Users/HP/Downloads/SFX/win.wav.mp3',        # Reach maze exit
            'game_over': 'C:/Users/HP/Downloads/SFX/game_over.wav.mp3', # Caught by enemy
            'hit': 'C:/Users/HP/Downloads/SFX/enemy_hit.wav.wav',      # Ammo hits enemy
            'shield': 'C:/Users/HP/Downloads/SFX/shield.wav.wav',      # Shield bonus (future)
            'stun': 'C:/Users/HP/Downloads/SFX/stun.wav.mp3',          # Enemy stunned
            'food': 'C:/Users/HP/Downloads/SFX/eat.wav.wav'            # Eat food/ammo
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                self.sounds[sound_name] = pygame.mixer.Sound(file_path)
            except:
                # Create silent sound if file not found
                self.sounds[sound_name] = pygame.mixer.Sound(buffer=b'\x00\x00' * 100)
                print(f"Sound file not found: {file_path}")
    
    def play(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume)
            sound.play()
    
    def start_background_music(self):
        """Start looped background music"""
        try:
            pygame.mixer.music.load('C:/Users/HP/Downloads/SFX/BGM.mp3')
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # Loop forever
        except:
            print("Background music file not found: BGM.mp3")
    
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """Set background music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)