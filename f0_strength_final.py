import pandas as pd
import numpy as np
import os

class DataProcessor:
    def __init__(self, directory, prefixes):
        self.directory = directory
        self.prefixes = prefixes

    def process_and_interpolate(self, file_path):
        processed_data = pd.read_csv(file_path)
        aggregated_df = processed_data.groupby('t', as_index=False).agg({
            'file': 'first',
            'f0_row1': 'mean',
            'strength_row1': 'mean',
            'strength_rowmax': 'mean'
        })
        aggregated_df['file'].fillna(method='ffill', inplace=True)
        aggregated_df['file'] = aggregated_df.apply(lambda row: self.prefixes if pd.isnull(row['file']) else row['file'], axis=1)
        aggregated_df['file'].fillna(method='bfill', inplace=True)

        all_time_points = pd.DataFrame({'t': np.arange(min(aggregated_df['t']), max(aggregated_df['t']) + 1)})
        merged_df = pd.merge(all_time_points, aggregated_df, on='t', how='left')

        interp_columns = ['strength_row1', 'strength_rowmax']
        for column in interp_columns:
            merged_df[column] = merged_df[column].interpolate()

        merged_df['file'].fillna(method='bfill', inplace=True)

        output_file = os.path.join('/content/Proper_project/data_tables/', f'{os.path.basename(file_path)}')
        merged_df.to_csv(output_file, index=False, float_format='%.2f')

    def process_files(self):
        for filename in os.listdir(self.directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.directory, filename)
                self.process_and_interpolate(file_path)
                print(f"Processed and interpolated file: {filename}")

# Example Usage:
directory_path = '/content/Proper_project/output_csv/'
prefix_pattern = ['AH_1','DM_1', 'glenn_1', 'joe_7', 'misc_58']  # Define the prefix pattern here

# Create an instance of the DataProcessor class
data_processor = DataProcessor(directory_path, prefix_pattern)

# Process and interpolate the files in the directory
data_processor.process_files()
