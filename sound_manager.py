import os
import pygame
import array
import math
import wave

class SoundManager:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Dictionary to store loaded sounds
        self.sounds = {}
        self.music_playing = False
        
        # Create sounds directory if it doesn't exist
        if not os.path.exists('sounds'):
            try:
                os.makedirs('sounds')
            except FileExistsError:
                # If it exists but is not a directory, handle the error
                if not os.path.isdir('sounds'):
                    print("Warning: 'sounds' exists but is not a directory")
                    
        # Create shop and inn sounds if they don't exist
        self.create_shop_sounds()
        self.create_inn_sounds()
        
    def load_sound(self, name, filename):
        """Load a sound effect and store it in the sounds dictionary"""
        if name not in self.sounds:
            try:
                sound_path = os.path.join('sounds', filename)
                self.sounds[name] = pygame.mixer.Sound(sound_path)
                return True
            except pygame.error:
                print(f"Could not load sound file: {filename}")
                return False
        return True
        
    def play_sound(self, name, sound_enabled=True):
        """Play a sound effect if it's loaded and sound is enabled"""
        if not sound_enabled:
            return
            
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Sound '{name}' not loaded")
            
    def play_music(self, filename, music_enabled=True):
        """Play background music if music is enabled"""
        if not music_enabled:
            return
            
        try:
            # Ensure previous music is stopped to avoid overlap
            pygame.mixer.music.stop()
            music_path = os.path.join('sounds', filename)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            self.music_playing = True
        except pygame.error:
            print(f"Could not load music file: {filename}")
            
    def stop_music(self):
        """Stop the currently playing background music"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            
    def set_music_volume(self, volume):
        """Set the volume of the background music (0.0 to 1.0)"""
        pygame.mixer.music.set_volume(volume)
        
    def set_sound_volume(self, name, volume):
        """Set the volume of a specific sound effect (0.0 to 1.0)"""
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
            
    def create_shop_sounds(self):
        """Create shop-specific sound files if they don't exist"""
        # Create buy sound
        buy_sound_path = os.path.join('sounds', 'buy.wav')
        if not os.path.exists(buy_sound_path):
            self._create_sound_file(buy_sound_path, frequency=880, duration=0.3)
            
        # Create shop background music
        shop_music_path = os.path.join('sounds', 'background_shop.wav')
        if not os.path.exists(shop_music_path):
            self._create_sound_file(shop_music_path, frequency=440, duration=10.0, is_music=True)

    def create_inn_sounds(self):
        """Create inn-specific sound files if they don't exist"""
        # Save sound
        save_sound_path = os.path.join('sounds', 'save.wav')
        if not os.path.exists(save_sound_path):
            self._create_sound_file(save_sound_path, frequency=600, duration=0.25)

        # Heal sound
        heal_sound_path = os.path.join('sounds', 'heal.wav')
        if not os.path.exists(heal_sound_path):
            self._create_sound_file(heal_sound_path, frequency=300, duration=0.4)

        # Inn background music
        inn_music_path = os.path.join('sounds', 'background_inn.wav')
        if not os.path.exists(inn_music_path):
            self._create_sound_file(inn_music_path, frequency=220, duration=10.0, is_music=True)
            
    def _create_sound_file(self, filepath, frequency=440, duration=1.0, is_music=False):
        """Create a WAV file with the given frequency and duration"""
        # Audio parameters
        sample_rate = 44100
        amplitude = 32767 * 0.3  # 30% of max amplitude to avoid clipping
        
        # Generate audio data
        num_samples = int(sample_rate * duration)
        audio_data = array.array('h')
        
        if is_music:
            # For music, create a more complex sound with multiple frequencies
            for i in range(num_samples):
                t = float(i) / sample_rate
                # Main melody
                value = math.sin(2.0 * math.pi * frequency * t) * amplitude * 0.5
                # Add harmonics
                value += math.sin(2.0 * math.pi * (frequency * 1.5) * t) * amplitude * 0.3
                value += math.sin(2.0 * math.pi * (frequency * 0.5) * t) * amplitude * 0.2
                # Ensure we don't exceed the range of a signed short
                value = max(-32767, min(32767, int(value)))
                audio_data.append(value)
        else:
            # For sound effects, use a simple sine wave
            for i in range(num_samples):
                t = float(i) / sample_rate
                value = math.sin(2.0 * math.pi * frequency * t) * amplitude
                # Add a decay to make it sound more natural
                decay = 1.0 - (float(i) / num_samples)
                value = max(-32767, min(32767, int(value * decay)))
                audio_data.append(value)
        
        # Write to WAV file
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
            wav_file.writeframes(audio_data.tobytes())