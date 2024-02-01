import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import ipywidgets as widgets
from IPython.display import display
from amfm_decompy.basic_tools import SignalObj
from amfm_decompy.pYAAPT import yaapt
import parselmouth

class SmoothingMethodPYAAPT:
    def __init__(self, audio_dir):
        self.OutDirPitchTier = "/content/Proper_project/praat_data/pitch_tiers/"
        self.audio_files = self.get_audio_files(audio_dir)
        self.file_name_index = {os.path.basename(file): idx for idx, file in enumerate(self.audio_files)}
        self.dropdown_file = widgets.Dropdown(options=list(self.file_name_index.keys()), description='Select Audio File:')
        self.dropdown_s = widgets.Dropdown(options=[50, 100, 500, 700, 1000, 1500, 2000, 2500, 3000, 3500, 10000, 20000, 30000], description='Select S:')
        self.output = widgets.Output()

        self.dropdown_file.observe(self.on_change, names='value')
        self.dropdown_s.observe(self.on_change, names='value')

    def get_audio_files(self, audio_dir):
        audio_files = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.endswith(".wav")]
        return audio_files

    def get_raw_f0(self, audio_file):
        sound = parselmouth.Sound(audio_file)
        duration_seconds = sound.get_total_duration()

        signal = SignalObj(audio_file)
        raw_f0_values = yaapt(signal, frame_length=40, tda_frame_length=40, f0_min=75, f0_max=600)

        # Ensure consistent length of time_series and raw_f0_values
        time_step = duration_seconds / (len(raw_f0_values.samp_values) - 1)
        time_series = np.arange(0, duration_seconds + time_step, time_step)

        return time_series, raw_f0_values.samp_values


    def smooth_f0(self, time_series, raw_f0_values, s):
        filtered_indices = raw_f0_values > 131
        t_filtered = time_series[filtered_indices]
        f0_filtered = raw_f0_values[filtered_indices]
        spline = UnivariateSpline(t_filtered, f0_filtered, s=s)
        smoothed_t_seconds = np.linspace(t_filtered.min(), t_filtered.max(), 6000)
        smoothed_f0 = spline(smoothed_t_seconds)
        return smoothed_t_seconds, smoothed_f0

    def process_audio(self, selected_file, s):
        audio_file = self.audio_files[self.file_name_index[selected_file]]
        raw_t_seconds, raw_f0 = self.get_raw_f0(audio_file)
        smoothed_t_seconds, smoothed_f0 = self.smooth_f0(raw_t_seconds, raw_f0, s)
        file_name = os.path.basename(audio_file)

        output_pitch_file_path = os.path.join(self.OutDirPitchTier, os.path.splitext(selected_file)[0] + ".PitchTier")

        with open(output_pitch_file_path, 'w') as f:
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
            plt.title(f"Audio File: {file_name} (s={s})")
            plt.tight_layout()
            plt.show()

    def on_change(self, change):
        self.output.clear_output()
        selected_file = self.dropdown_file.value
        s = self.dropdown_s.value
        self.process_audio(selected_file, s)

    def display_dropdown(self):
        display(self.dropdown_file)
        display(self.dropdown_s)
        display(self.output)

# Example usage:
if __name__ == "__main__":
    audio_directory = "/content/Proper_project/praat_data/audio"
    smoothing_instance = SmoothingMethodPYAAPT(audio_directory)
    smoothing_instance.display_dropdown()
