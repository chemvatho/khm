import os
import parselmouth
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

# Praat pitch extraction parameters
time_step_pitch = 0.001

class PitchExtractor:
    def __init__(self, audio_directory, output_directory):
        self.audio_directory = audio_directory
        self.output_directory = output_directory
        self.time_step_pitch = time_step_pitch

    def process_pitch_object(self, pitch_object, current_file, smooth_value):
        time = np.round(pitch_object.xs(), 3) * 1000
        pitch_ceiling = 1000

        # Smooth track
        smooth_pitch = pitch_object.smooth(smooth_value)
        interpolated_pitch = smooth_pitch.interpolate().smooth(smooth_value)

        # Get the smoothed f0_row1
        smooth_f0_row1 = interpolated_pitch.selected_array['frequency']

        # Replace NaN values in smooth_f0_row1 with 0
        smooth_f0_row1[np.isnan(smooth_f0_row1)] = 0

        freqArray = pitch_object.selected_array['frequency']
        strength_row1 = pitch_object.selected_array['strength']

        # Replace NaN values in strength_row1 with 0
        strength_row1[np.isnan(strength_row1)] = 0

        zero_one_freqs = np.where(freqArray > pitch_ceiling, 0, 1)

        # Apply conditions for strength_rowmax
        strength_rowmax = strength_row1

        return pd.DataFrame({
            'file': current_file,
            't': time.astype(int),
            'f0_row1': np.round(smooth_f0_row1, 2),
            'strength_row1': np.round(strength_row1, 7),
            'strength_rowmax': np.round(strength_rowmax, 7)
        })

    def extract_pitch(self, pitch_floor_value, smooth_value):
        audio_files = os.listdir(self.audio_directory)
        wav_files = [file for file in audio_files if file.lower().endswith(".wav")]

        # Dropdown for selecting audio file
        file_dropdown = widgets.Dropdown(
            options=wav_files,
            description='Select audio file:',
            value=wav_files[0]
        )

        # Slider for pitch_floor
        pitch_floor_slider = widgets.IntSlider(
            value=pitch_floor_value,
            min=1,
            max=100,
            step=1,
            description='Pitch Floor:',
            style={'description_width': 'initial'}
        )

        # Slider for smooth
        smooth_slider = widgets.IntSlider(
            value=smooth_value,
            min=1,
            max=100,
            step=1,
            description='Smooth:',
            style={'description_width': 'initial'}
        )

        # Output widget for displaying information
        output_widget = widgets.Output()

        # Event handler for dropdown change
        def on_dropdown_change(change):
            with output_widget:
                clear_output(wait=True)  # Clear only the output related to plotting

                wav_file = change['new']
                soundFile = os.path.join(self.audio_directory, wav_file)
                current_file = os.path.splitext(wav_file)[0]
                sound = parselmouth.Sound(soundFile)

                pitch = sound.to_pitch_ac(
                    time_step=0.001, pitch_floor=pitch_floor_slider.value, max_number_of_candidates=15,
                    very_accurate=True, silence_threshold=0.03, voicing_threshold=0.25,
                    octave_cost=0.02, octave_jump_cost=0.5, voiced_unvoiced_cost=0.20,
                    pitch_ceiling=600.0
                )

                processed_data = self.process_pitch_object(pitch, current_file, smooth_slider.value)
                output_filename = os.path.join(self.output_directory, f"{current_file}_Pitch_strength_data.csv")
                processed_data.to_csv(output_filename, index=False)

                # Plotting strength_row1 and strength_rowmax
                plt.figure(figsize=(12, 6))

                plt.subplot(2, 1, 1)
                plt.plot(processed_data['t'], processed_data['strength_row1'], label='strength_row1')
                plt.title('strength_row1')
                plt.xlabel('Time (ms)')
                plt.ylabel('Strength')
                plt.legend()

                plt.subplot(2, 1, 2)
                plt.plot(processed_data['t'], processed_data['strength_rowmax'], label='strength_rowmax', color='orange')
                plt.title('strength_rowmax')
                plt.xlabel('Time (ms)')
                plt.ylabel('Strength')
                plt.legend()

                plt.tight_layout()
                plt.show()

                print(f"Processed data saved to: {output_filename} and plots displayed.")

        def on_slider_change(change):
            # Trigger the dropdown change event when any slider changes to update the plot
            on_dropdown_change({'new': file_dropdown.value})

        file_dropdown.observe(on_dropdown_change, names='value')
        pitch_floor_slider.observe(on_slider_change, names='value')
        smooth_slider.observe(on_slider_change, names='value')

        display(file_dropdown, pitch_floor_slider, smooth_slider, output_widget)

