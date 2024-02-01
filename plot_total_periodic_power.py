import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets
import os

class DataPlotter:
    def __init__(self, merged_directory):
        self.merged_directory = merged_directory
        self.merged_data = self._load_merged_data()

        self.file_dropdown = widgets.Dropdown(options=list(self.merged_data.keys()), description='Select File')
        interact(self.plot_selected_file, file_name=self.file_dropdown)

    def _load_merged_data(self):
        merged_files = [file for file in os.listdir(self.merged_directory) if file.endswith('_merged.csv')]
        data = {}
        for file in merged_files:
            file_prefix = file.split('_')[0]
            file_path = os.path.join(self.merged_directory, file)
            data[file_prefix] = pd.read_csv(file_path)
        return data

    def plot_selected_file(self, file_name):
        plt.figure(figsize=(8, 6))

        selected_data = self.merged_data[file_name]

        #print("Available columns:", selected_data.columns)

        if 't' in selected_data.columns and 'total_power' in selected_data.columns and 'periodic_power' in selected_data.columns:
            #print("Example periodic_power values:", selected_data['periodic_power'].head())

            plt.plot(selected_data['t'], selected_data['total_power'], label='Total Power')
            plt.plot(selected_data['t'], selected_data['periodic_power'], label='Periodic Power')

            plt.title('Total Power vs Periodic Power')
            plt.xlabel('Time')
            plt.ylabel('Power')
            plt.legend()
            plt.show()
        else:
            print("Required columns ('t', 'total_power', 'periodic_power') not found in the selected file.")

# Usage:

