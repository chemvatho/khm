import os
import numpy as np
import pandas as pd
import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import clear_output
from matplotlib.collections import LineCollection

yScale1 = ['speakerScale', 'tokenScale', 'dataScale']  # Choose the appropriate value here

class F0Plotter:
    def __init__(self, file_prefixes, data_path):
        self.file_prefixes = file_prefixes
        self.data_path = data_path
        self.dropdown = widgets.Dropdown(options=self.file_prefixes, description='Select Prefix:')
        self.dropdown.observe(self.plot_files, names='value')
        self.all_files = os.listdir(data_path)  # Update all_files attribute here

    def plot_files(self, change):
        print("Plotting new file...")  # Add this line for debugging
        selected_prefix = change['new']
        files_to_plot = [file for file in self.all_files if file.startswith(selected_prefix)]

        # Clear previous output and plot
        clear_output(wait=True)

        # Display the dropdown again after plotting
        display(self.dropdown)

        for sel_file in files_to_plot:
            file_path = os.path.join(self.data_path, sel_file)
            single_token1 = pd.read_csv(file_path)

            plotFloor1 = single_token1['plotFloorToken'].iloc[0] if yScale1 == 'tokenScale' else \
                 single_token1['plotFloorSpeaker'].iloc[0] if yScale1 == 'speakerScale' else \
                 single_token1['plotFloorData'].iloc[0]

            plotUnits1 = round(single_token1['f0_token_range'].iloc[0] / 30) if yScale1 == 'tokenScale' else \
                        round(single_token1['f0_speaker_range'].iloc[0] / 30) if yScale1 == 'speakerScale' else \
                        round(single_token1['f0_data_range'].iloc[0] / 30)

            f0range1 = single_token1['f0_token_range'].iloc[0] if yScale1 == 'tokenScale' else \
                      single_token1['f0_speaker_range'].iloc[0] if yScale1 == 'speakerScale' else \
                      single_token1['f0_data_range'].iloc[0]

            f0max1 = single_token1['f0_token_max'].iloc[0] if yScale1 == 'tokenScale' else \
                    single_token1['f0_speaker_max'].iloc[0] if yScale1 == 'speakerScale' else \
                    single_token1['f0_data_max'].iloc[0]

            periogram_single1 = plt.figure()

            # Your plotting code...
            fig = plt.figure(figsize=(12, 8))

            # Sample data (replace with your actual data)
            x = single_token1['t']
            y = single_token1['f0_interp_stretch_smooth']
            alphas = single_token1['smogPP_20Hz']

            # Calculate linewidths based on data range
            linewidths = alphas * 14

            #colors = plt.cm.Greys(linewidths)  # Using a colormap for colors, you can choose other colormaps too
            colors = plt.cm.YlOrRd(alphas)

            # Set color to gray (RGB value)
            segment_color = [0.1, 0.1, 0.1]  # RGB values for gray

            # Define a threshold for segmentation
            threshold =  0.00000000001 # Adjust this threshold value as needed

            # Split data into segments based on threshold
            segment_indices = np.where(alphas > threshold)[0]
            segments = np.split(segment_indices, np.where(np.diff(segment_indices) != 1)[0] + 1)

            # Create LineCollection for each segment
            for segment in segments:
                segment_x = x[segment]
                segment_y = y[segment]
                segment_linewidths = linewidths[segment]
                segment_alphas = alphas[segment]
                segment_colors = colors[segment]

                points = np.array([segment_x, segment_y]).T.reshape(-1, 1, 2)
                segment_segments = np.concatenate([points[:-1], points[1:]], axis=1)

                # Create LineCollection with specified color and add to plot
                lc = LineCollection(segment_segments, linewidth=segment_linewidths, alpha=segment_alphas, color=segment_colors)
                plt.gca().add_collection(lc)

            plt.plot(single_token1['t'], single_token1['postPP_rel'] * f0range1 + plotFloor1,
                    color="blue", alpha=1, linewidth=1, linestyle="solid")

            plt.plot(single_token1['t'], single_token1['smogPP_5Hz'] * f0range1 + plotFloor1,
                    color="brown", alpha=1, linewidth=2)

            if len(single_token1['syll_label']) > 0:
                plt.vlines(single_token1['syll_bounds'], ymin=plotFloor1, ymax=f0max1 + plotUnits1 * 2,
                          linestyles="dotted", colors="blue", linewidth=0.8, alpha=0.8)

                # Add dashed lines at the ends of syllable bounds
                for bound in single_token1['syll_end']:
                    plt.plot([bound, bound], [plotFloor1, f0max1 + plotUnits1 * 2], linestyle='--', color='blue', linewidth=0.5, alpha=0.5)

            # Existing code for syllable mid labels
            if len(single_token1['syll_mid']) > 0:
                for x, label in zip(single_token1['syll_mid'], single_token1['syll_label']):
                    if pd.notna(x) and pd.notna(label):  # Check for valid values
                        plt.text(x, f0max1 + plotUnits1 * 2, str(label), size=10, color="red", family="serif")

            plt.title(sel_file)  # Updated this line to use sel_file as the plot title
            plt.xlabel("Time (ms)")
            plt.ylabel("F0 (Hz)")
            plt.ylim(plotFloor1, f0max1 + plotUnits1 * 5)
            plt.show()


# Example usage:
data_file_path = "/content/Proper_project/PerEnergy_F0Curves/"

file_prefixes = ['AH_1', 'DM_1', 'glenn_1', 'joe_7', 'misc_58', 'Khm_1']

# Assuming your files are named using the prefixes in the specified directory
all_files = os.listdir(data_file_path)

f0_plotter = F0Plotter(file_prefixes, data_file_path)
f0_plotter.all_files = all_files
display(f0_plotter.dropdown)
