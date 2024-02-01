import os
import glob
import parselmouth
import math
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

class Praat_PitchAnalysis:
    def __init__(self, in_dir_audio, out_dir_pitch_tier):
        self.in_dir_audio = in_dir_audio
        self.out_dir_pitch_tier = out_dir_pitch_tier
        self.sound_files = glob.glob(os.path.join(self.in_dir_audio, "*.wav"))

        self.dropdown_file = widgets.Dropdown(options=self._get_file_names(), description='Select Audio File:')
        self.slider_pitch_floor = widgets.FloatSlider(value=40, min=1, max=100, step=1, description='Pitch Floor:')
        self.slider_smooth = widgets.FloatSlider(value=10, min=1, max=100, step=1, description='Smooth:')
        self.button_process = widgets.Button(description='Process and Plot')
        self.output = widgets.Output()

        self.dropdown_file.observe(self.on_change, names='value')
        self.slider_pitch_floor.observe(self.on_change_params, names='value')
        self.slider_smooth.observe(self.on_change_params, names='value')
        self.button_process.on_click(self.on_button_click)

    def _get_file_names(self):
        return [os.path.basename(file) for file in self.sound_files]

    def process_audio(self, sound_file, pitch_floor=40, smooth=10):
        with self.output:
            clear_output(wait=True)  # Clear previous output

            current_file = os.path.splitext(os.path.basename(sound_file))[0]
            sound = parselmouth.Sound(sound_file)

            pitch = sound.to_pitch_ac(
                time_step=0.001, pitch_floor=pitch_floor, max_number_of_candidates=15,
                very_accurate=True, silence_threshold=0.03, voicing_threshold=0.25,
                octave_cost=0.02, octave_jump_cost=0.5, voiced_unvoiced_cost=0.20,
                pitch_ceiling=600.0
            )

            smooth_pitch = pitch.smooth(smooth)
            interpolated_pitch = smooth_pitch.interpolate().smooth(smooth)

            smooth_data = np.column_stack((interpolated_pitch.xs(), interpolated_pitch.selected_array['frequency']))
            smooth_csv_path = os.path.join(self.out_dir_pitch_tier, current_file + "_smooth.csv")
            np.savetxt(smooth_csv_path, smooth_data, delimiter=",", header="Time (s), Frequency (Hz)", comments="")

            output_pitch_file_path = os.path.join(self.out_dir_pitch_tier, current_file + ".PitchTier")

            with open(output_pitch_file_path, 'w') as f:
                for time, frequency in zip(interpolated_pitch.xs(), interpolated_pitch.selected_array['frequency']):
                    if not isinstance(frequency, float) or math.isnan(frequency) or frequency < 30:
                        continue

                    f.write(f"{time}\n")
                    f.write(f"{frequency}\n")

            print(f"Processing complete for sound file: {sound_file}")

            plt.figure(figsize=(12, 8))
            plt.plot(pitch.xs(), pitch.selected_array['frequency'], 'o', markersize=3, label="Original")
            plt.plot(interpolated_pitch.xs(), interpolated_pitch.selected_array['frequency'], 'r.', markersize=2,
                     label="Smoothed")

            plt.xlim(min(pitch.xs()), max(pitch.xs()))
            plt.ylim(0, 600)
            plt.xlabel("Time (s)")
            plt.ylabel("Frequency (Hz)")
            plt.legend()
            plt.title("F0 Contour for " + current_file)
            plt.box(False)
            plt.grid(True)
            plt.show()

    def on_change(self, change):
        # Do nothing here, let the user choose the audio file
        pass

    def on_change_params(self, change):
        # Do nothing here, let the user adjust slider values
        pass

    def on_button_click(self, button):
        sound_file_path = os.path.join(self.in_dir_audio, self.dropdown_file.value)
        pitch_floor = self.slider_pitch_floor.value
        smooth = self.slider_smooth.value
        self.process_audio(sound_file_path, pitch_floor, smooth)

    def display_widgets(self):
        display(self.dropdown_file)
        display(self.slider_pitch_floor)
        display(self.slider_smooth)
        display(self.button_process)
        display(self.output)

# Example usage:
if __name__ == "__main__":
    InDirAudio = "/content/Proper_project/praat_data/audio"
    OutDirPitchTier = "/content/Proper_project/praat_data/pitch_tiers/"

    pitch_analysis = Praat_PitchAnalysis(InDirAudio, OutDirPitchTier)
    pitch_analysis.display_widgets()
