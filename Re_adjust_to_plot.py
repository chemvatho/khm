import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import os

class Datadjust:
    def __init__(self, directory):
        self.directory = directory
        self.output_directory = os.path.join(directory, "Re_adjust")
        os.makedirs(self.output_directory, exist_ok=True)

    def butter_lowpass(self, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def process_files(self, file_prefixes):
        fs = 1000  # Assuming the sampling frequency is 1000 Hz
        max_token_per_power = 0.01  # Replace with your actual value
        max_data_per_power = 0.01  # Replace with your actual value
        max_speaker_per_power = 0.01  # Replace with your actual value

        cutoff_frequencies = [20, 12, 8, 5]

        for prefix in file_prefixes:
            file_path = os.path.join(self.directory, f"{prefix}_processed.csv")
            if os.path.exists(file_path):
                main_df = pd.read_csv(file_path)

                files = main_df['file'].unique()
                if len(files) == 1:
                    main_df['perFloorStatus'] = np.where(
                        main_df['file'] == files[0], 0.004,
                        main_df['perFloorStatus']
                    )
                elif len(files) >= 2:
                    main_df['perFloorStatus'] = np.where(
                        main_df['file'] == files[0], 0.004,
                        np.where(main_df['file'] == files[1], 0.04, main_df['perFloorStatus'])
                    )
                    # Add more conditions for other unique file names if necessary

                main_df['perFloor_indeed'] = np.where(
                    main_df['relToStatus'] == 'token',
                    np.round(max_token_per_power * main_df['perFloorStatus'], 10),
                    np.where(
                        main_df['relToStatus'] == 'data',
                        np.round(max_data_per_power * main_df['perFloorStatus'], 10),
                        np.round(max_speaker_per_power * main_df['perFloorStatus'], 10)
                    )
                )

                main_df['logPP'] = 10 * np.log10(main_df['postPP'] / main_df['perFloor_indeed'])
                main_df['logPP'] = np.where((main_df['logPP'] < 0) | (main_df['logPP'].isna()), 0, main_df['logPP'])

                for cutoff in cutoff_frequencies:
                    column_name = f"smogPP_{cutoff}Hz"
                    filtered_column = self.butter_lowpass_filter(main_df['logPP'], cutoff, fs)
                    main_df[column_name] = np.where(filtered_column < 0, 0, np.round(filtered_column / max(filtered_column), 5))

                output_file_path = os.path.join(self.output_directory, f"{prefix}_adjusted.csv")
                main_df.to_csv(output_file_path, index=False)
                print(f"File {prefix}_adjusted.csv saved in Re_adjust folder.")
            else:
                print(f"File for prefix {prefix} not found.")

# Example usage:
directory_path = "/content/Proper_project/PerEnergy_F0Curves/"
file_prefixes = ['AH_1', 'DM_1', 'glenn_1', 'joe_7', 'misc_58', 'Khm_1']

processor = Datadjust(directory_path)
processor.process_files(file_prefixes)
