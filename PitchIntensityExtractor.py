import os
import glob
import parselmouth
import math

class PitchIntensityExtractor:
    def __init__(self, in_dir_audio, out_dir_intensity_tier, out_dir_pitch_object, out_dir_pitch_tier):
        self.in_dir_audio = in_dir_audio
        self.out_dir_intensity_tier = out_dir_intensity_tier
        self.out_dir_pitch_object = out_dir_pitch_object
        self.out_dir_pitch_tier = out_dir_pitch_tier

        # Create directories if they don't exist
        os.makedirs(self.out_dir_intensity_tier, exist_ok=True)
        os.makedirs(self.out_dir_pitch_object, exist_ok=True)
        os.makedirs(self.out_dir_pitch_tier, exist_ok=True)

    def process_files(self):
        # List WAV files
        sound_files = [f for f in os.listdir(self.in_dir_audio) if f.endswith(".wav")]

        # Loop through each WAV file
        for sound_file in sound_files:
            current_file = os.path.splitext(sound_file)[0]
            sound = parselmouth.Sound(os.path.join(self.in_dir_audio, sound_file))

            # Extract pitch
            pitch = self._extract_pitch(sound, current_file)

            # Extract intensity
            self._extract_intensity(sound, current_file)

            # Create pitch tier
            self._create_pitch_tier(sound_file, current_file, pitch)

    def _extract_pitch(self, sound, current_file):
        # Praat pitch extraction parameters
        time_step_pitch = 0.001
        silence_thr = 0.03
        voicing_thr = 0.2
        octave = 0.02
        octave_jump = 0.5
        voice_unvoiced = 0.14
        pitch_max = 600.0

        # Create pitch object and save
        pitch = sound.to_pitch_ac(time_step=time_step_pitch, pitch_floor=38, max_number_of_candidates=14,
                                  very_accurate=True, silence_threshold=silence_thr, voicing_threshold=voicing_thr,
                                  octave_cost=octave, octave_jump_cost=octave_jump, voiced_unvoiced_cost=voice_unvoiced,
                                  pitch_ceiling=pitch_max)
        pitch.save(os.path.join(self.out_dir_pitch_object, current_file + ".Pitch"))
        return pitch

    def _extract_intensity(self, sound, current_file):
        # Extract intensity
        time_step_intensity = 0.001
        starting_time = 0

        intensity = sound.to_intensity(time_step=time_step_intensity, minimum_pitch=40, subtract_mean=True)
        time_points = intensity.xs() + starting_time
        intensity_values = intensity.values.flatten()

        with open(os.path.join(self.out_dir_intensity_tier, current_file + ".IntensityTier"), "w") as f:
            for t, i in zip(time_points, intensity_values):
                f.write("{:.6f}\n{:.6f}\n".format(t, i))

    def _create_pitch_tier(self, sound_file, current_file, pitch):
        # Extract pitch values from the pitch object
        time_points = pitch.xs()
        pitch_values = pitch.selected_array['frequency']

        # Create the output file path for pitch tier
        output_pitch_file_path = os.path.join(self.out_dir_pitch_tier, current_file + ".PitchTier")

        # Open the output file for writing
        with open(output_pitch_file_path, 'w') as f:
            for time, frequency in zip(time_points, pitch_values):
                # Check for NaN values or values below pitch_floor
                if not isinstance(frequency, float) or math.isnan(frequency) or frequency < 40:
                    continue  # Skip writing this point

                # Write time and pitch value in the format required by .PitchTier files
                f.write(f"{time}\n")
                f.write(f"{frequency}\n")

        print(f"Processing complete for sound file: {sound_file}")