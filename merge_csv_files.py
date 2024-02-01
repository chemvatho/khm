import os
import pandas as pd

class DataMerger:
    def __init__(self, prefixes):
        self.prefixes = prefixes

    def merge_data(self):
        for prefix in self.prefixes:
            fullTime_data = pd.read_csv(f"/content/Proper_project/data_tables/{prefix}_fullTime_data.csv")
            intensity_data = pd.read_csv(f"/content/Proper_project/data_tables/{prefix}_intensity_data.csv")
            f0_smooth_data = pd.read_csv(f"/content/Proper_project/data_tables/{prefix}_f0_smooth_data.csv")
            pitchObject_data = pd.read_csv(f"/content/Proper_project/data_tables/{prefix}_Pitch_strength_data.csv")

            textGridSyll_csv_exists = os.path.exists(f"/content/Proper_project/data_tables/{prefix}_syllable_data.csv")
            textGridWord_csv_exists = os.path.exists(f"/content/Proper_project/data_tables/{prefix}_word_data.csv")

            try:
                textGridSyll_df = pd.read_csv(f"/content/Proper_project/data_tables/{prefix}_syllable_data.csv")
            except FileNotFoundError:
                textGridSyll_csv_exists = False

            try:
                textGridWord_df = pd.read_csv(f"/content/Proper_project/data_tables/{prefix}_word_data.csv")
            except FileNotFoundError:
                textGridWord_csv_exists = False

            raw_df = fullTime_data.merge(intensity_data, on=["file", "t"], how="outer")
            raw_df = raw_df.merge(f0_smooth_data, on=["file", "t"], how="outer")
            raw_df = raw_df.merge(pitchObject_data, on=["file", "t"], how="outer")

            if textGridSyll_csv_exists:
                raw_df = raw_df.merge(textGridSyll_df, on=["file", "t"], how="outer")
            if textGridWord_csv_exists:
                raw_df = raw_df.merge(textGridWord_df, on=["file", "t"], how="outer")

            raw_df.dropna(subset=["t"], inplace=True)

            raw_df['total_power'] = round(4e-10 * 10**(raw_df['intensity'] / 10), 9)
            raw_df['periodic_power'] = round(raw_df['total_power'] * raw_df['strength_rowmax'], 9)

            # Write merged_df to a separate CSV file with the prefix in the filename
            raw_df.to_csv(f"/content/Proper_project/data_tables/{prefix}_merged.csv", index=False)

# Usage:
prefixes = ['AH_1','DM_1', 'glenn_1', 'joe_7', 'misc_58']
data_merger = DataMerger(prefixes)
data_merger.merge_data()
