import os
import numpy as np
import pandas as pd
import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import clear_output
from scipy.interpolate import UnivariateSpline
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

y_scale1 = ['speakerScale', 'tokenScale', 'dataScale']  # Choose the appropriate value here

class F0_No_Effect_Plotter:
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

        fig, axes = plt.subplots(nrows=len(files_to_plot), ncols=1, figsize=(12, 8 * len(files_to_plot)), squeeze=False)

        for i, sel_file1 in enumerate(files_to_plot):
            file_path = os.path.join(self.data_path, sel_file1)
            single_token1 = pd.read_csv(file_path)

            plotFloor1 = single_token1['plotFloorToken'].iloc[0] if y_scale1 == 'tokenScale' else \
                 single_token1['plotFloorSpeaker'].iloc[0] if y_scale1 == 'speakerScale' else \
                 single_token1['plotFloorData'].iloc[0]

            plotUnits1 = round(single_token1['f0_token_range'].iloc[0] / 30) if y_scale1 == 'tokenScale' else \
                        round(single_token1['f0_speaker_range'].iloc[0] / 30) if y_scale1 == 'speakerScale' else \
                        round(single_token1['f0_data_range'].iloc[0] / 30)

            f0range1 = single_token1['f0_token_range'].iloc[0] if y_scale1 == 'tokenScale' else \
                      single_token1['f0_speaker_range'].iloc[0] if y_scale1 == 'speakerScale' else \
                      single_token1['f0_data_range'].iloc[0]

            f0max1 = single_token1['f0_token_max'].iloc[0] if y_scale1 == 'tokenScale' else \
                    single_token1['f0_speaker_max'].iloc[0] if y_scale1 == 'speakerScale' else \
                    single_token1['f0_data_max'].iloc[0]

            time_series = single_token1['t'].values
            f0_values = single_token1['f0_interp'].values

            valid_indices = np.logical_and(np.isfinite(f0_values), ~np.isnan(f0_values))
            time_series = time_series[valid_indices]
            f0_values = f0_values[valid_indices]

            # Inside the for loop where LineCollection is used
            cmap = LinearSegmentedColormap.from_list("", [(0, 0, 0), (0, 0, 0)])

            smooth_time = np.linspace(time_series.min(), time_series.max(), num=100)
            spl = UnivariateSpline(time_series, f0_values, s=1000)
            smooth_f0_values = spl(smooth_time)

            min_line_width = 13
            max_line_width = 13
            normalized_f0 = (f0_values - f0_values.min()) / (f0_values.max() - f0_values.min())
            line_widths = min_line_width + normalized_f0 * (max_line_width - min_line_width)

            points = np.array([smooth_time, smooth_f0_values]).T
            segments = np.array([points[:-1], points[1:]]).transpose(1, 0, 2)

            # Generate colors from the colormap based on the normalized values
            colors = cmap(normalized_f0)  # Use normalized_f0 values to get colors from the colormap

            lc = LineCollection(segments, color=colors, linewidth=line_widths)

            # Rest of your plotting c
            ax = axes[i][0]  # Access the specific axis for this iteration

            ax.plot(single_token1['t'], single_token1['postPP_rel'] * f0range1 + plotFloor1,
                         color="darkblue", alpha=1, linewidth=0.5, linestyle="-.", label='postPP_rel')

            ax.plot(single_token1['t'], single_token1['smogPP_20Hz'] * f0range1 + plotFloor1,
                         color="magenta", alpha=0.3, linewidth=2, label='smogPP_5Hz')

            if len(single_token1['syll_bounds']) > 0:
                ax.vlines(single_token1['syll_bounds'], ymin=plotFloor1, ymax=f0max1 + plotUnits1 * 2,
                              linestyles="dotted", colors="darkblue", linewidth=0.5, alpha=1, label='syllable_bounds')
                for bound in single_token1['syll_end']:
                    ax.plot([bound, bound], [plotFloor1, f0max1 + plotUnits1 * 2], linestyle='--', color='blue', linewidth=0.5, alpha=0.5)

            if len(single_token1['syll_mid']) > 0:
                for x, label in zip(single_token1['syll_mid'], single_token1['syll_label']):
                    if pd.notna(x) and pd.notna(label):
                        ax.text(x, f0max1 + plotUnits1 * 2, str(label), size=8, color="red", family="serif")

            ax.add_collection(lc)
            ax.autoscale()

            ax.set_xlim()
            ax.set_ylim(f0_values.min(), f0_values.max())
            ax.set_title(sel_file1, color="white")
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("F0 (Hz)")
            ax.set_ylim(plotFloor1, f0max1 + plotUnits1 * 9)

            ax.set_facecolor("white")
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='x', colors='gray')
            ax.tick_params(axis='y', colors='gray')
            
            ax.plot([], [], color="black", label='f0')
            ax.legend()

        plt.tight_layout()
        plt.show()

# Example usage:
data_file_path = "/content/Proper_project/PerEnergy_F0Curves/"
file_prefixes = ['AH_1', 'DM_1', 'glenn_1', 'joe_7', 'misc_58']
all_files = os.listdir(data_file_path)

f0_plotter = F0_No_Effect_Plotter(file_prefixes, data_file_path)
f0_plotter.all_files = all_files
display(f0_plotter.dropdown)