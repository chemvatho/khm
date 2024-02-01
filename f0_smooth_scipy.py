import os
import parselmouth
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import ipywidgets as widgets
from IPython.display import display

class SmoothingMethodScipy:
    def __init__(self, audio_dir):
        self.OutDirPitchTier = "/content/Proper_project/praat_data/pitch_tiers/"  # Define here
        self.audio_files = self.get_audio_files(audio_dir)
        self.file_name_index = {os.path.basename(file): idx for idx, file in enumerate(self.audio_files)}
        self.dropdown = widgets.Dropdown(options=list(self.file_name_index.keys()), description='Select Audio File:')
        self.output = widgets.Output()
        self.dropdown.observe(self.on_change, names='value')

    def get_audio_files(self, audio_dir):
        audio_files = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.endswith(".wav")]
        return audio_files

    def get_raw_f0(self, audio_file):
        audio = parselmouth.Sound(audio_file)
        pitch = audio.to_pitch()
        raw_f0_values = np.array(pitch.selected_array['frequency'])
        time_step = audio.xmax / len(raw_f0_values)
        time_series = np.arange(0, audio.xmax, time_step)
        return time_series, raw_f0_values

    def smooth_f0(self, time_series, raw_f0_values):
        filtered_indices = raw_f0_values > 131
        t_filtered = time_series[filtered_indices]
        f0_filtered = raw_f0_values[filtered_indices]
        s = 1000  # Adjust this value for desired smoothness
        spline = UnivariateSpline(t_filtered, f0_filtered, s=s)
        smoothed_t_seconds = np.linspace(t_filtered.min(), t_filtered.max(), 6000)
        smoothed_f0 = spline(smoothed_t_seconds)
        return smoothed_t_seconds, smoothed_f0

    def process_audio(self, selected_file):
        audio_file = self.audio_files[self.file_name_index[selected_file]]
        raw_t_seconds, raw_f0 = self.get_raw_f0(audio_file)
        smoothed_t_seconds, smoothed_f0 = self.smooth_f0(raw_t_seconds, raw_f0)
        file_name = os.path.basename(audio_file)
        
        
        # Derive the output file name from the selected file
        output_pitch_file_path = os.path.join("/content/Proper_project/praat_data/pitch_tiers", os.path.splitext(selected_file)[0] + ".PitchTier")

        # Open the output file for writing
        with open(output_pitch_file_path, 'w') as f:
            # Write time and pitch values
            for time, frequency in zip(smoothed_t_seconds, smoothed_f0):
                f.write(f"{time}\n")
                f.write(f"{frequency}\n")

        with self.output:
            plt.figure(figsize=(10, 6))
            plt.scatter(raw_t_seconds, raw_f0, label='Original F0', color='blue', alpha=0.3)
            plt.plot(smoothed_t_seconds, smoothed_f0, label='Smoothed F0', color='red')
            plt.xlabel('Time (s)')
            plt.ylabel('F0')
            plt.xlim(0, 3)
            plt.ylim(0, 600)
            plt.legend()
            plt.title(f"Audio File: {file_name}")
            plt.tight_layout()
            plt.show()

    def on_change(self, change):
        self.output.clear_output()
        selected_file = change['new']
        self.process_audio(selected_file)

    def display_dropdown(self):
        display(self.dropdown)
        display(self.output)

# Example usage:
if __name__ == "__main__":
    
    audio_directory = "/content/Proper_project/praat_data/audio"
    smoothing_instance = SmoothingMethodScipy(audio_directory)
    smoothing_instance.display_dropdown()