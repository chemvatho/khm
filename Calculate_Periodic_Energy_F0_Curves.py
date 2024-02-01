import os
import numpy as np
import pandas as pd
from scipy import signal
from scipy.signal import filtfilt
from scipy.signal import butter, lfilter


class DataProcessor:
    def __init__(self, input_dir, output_dir, prefixes):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.prefixes = prefixes

    def bwfilter(self, wave, f, to, n):
        b, a = signal.butter(n, to / (f / 2), btype='low')
        return signal.lfilter(b, a, wave)

    def process_data(self):
        import numpy as np
        from scipy import signal

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for prefix in prefixes:
            filename = f"{InputDir}/{prefix}_merged.csv"
            if os.path.exists(filename):
                raw_df = pd.read_csv(filename)  # Load your data
                main_df = raw_df.copy()

                perFloor = 0.01
                relTo = 'speaker' #['data', 'speaker', 'token']
                strengThresh = 0.25

                main_df['perFloorStatus'] = perFloor
                main_df['relToStatus'] = relTo
                main_df['strengThreshStatus'] = strengThresh

                main_df['max_data_per_power'] = main_df['periodic_power'].max()
                main_df['max_data_strength'] = main_df['strength_rowmax'].max()
                main_df['f0_data_min'] = np.round(main_df['f0_smooth'].min())
                main_df['f0_data_max'] = np.round(main_df['f0_smooth'].max())
                main_df['f0_data_range'] = np.round(main_df['f0_data_max'] - main_df['f0_data_min'])

                if 'speaker' in main_df.columns:
                    speaker_group = main_df.groupby('speaker')
                    main_df = main_df.join(speaker_group['periodic_power'].transform('max').rename('max_speaker_per_power'))
                    main_df = main_df.join(speaker_group['strength_rowmax'].transform('max').rename('max_speaker_strength'))
                    main_df = main_df.join(speaker_group['f0_smooth'].transform('min').round().rename('f0_speaker_min'))
                    main_df = main_df.join(speaker_group['f0_smooth'].transform('max').round().rename('f0_speaker_max'))
                    main_df = main_df.join(speaker_group['f0_smooth'].transform('median').round().rename('f0_speaker_median'))
                    main_df = main_df.join(speaker_group['f0_smooth'].transform('mean').round().rename('f0_speaker_mean'))
                    main_df = main_df.join((main_df['f0_speaker_max'] - main_df['f0_speaker_min']).round().rename('f0_speaker_range'))

                token_group = main_df.groupby('file')
                main_df = main_df.join(token_group['periodic_power'].transform('max').rename('max_token_per_power'))
                main_df = main_df.join(token_group['strength_rowmax'].transform('max').rename('max_token_strength'))
                main_df = main_df.join(token_group['f0_smooth'].transform('min').round().rename('f0_token_min'))
                main_df = main_df.join(token_group['f0_smooth'].transform('max').round().rename('f0_token_max'))
                main_df = main_df.join(token_group['f0_smooth'].transform('median').round().rename('f0_token_median'))
                main_df = main_df.join(token_group['f0_smooth'].transform('mean').round().rename('f0_token_mean'))
                main_df = main_df.join((main_df['f0_token_max'] - main_df['f0_token_min']).round().rename('f0_token_range'))

                main_df['plotFloorToken'] = (main_df['f0_token_min'] - main_df['f0_token_range']).round()
                main_df['plotFloorSpeaker'] = (main_df['f0_speaker_min'] - main_df['f0_speaker_range']).round()
                main_df['plotFloorData'] = (main_df['f0_data_min'] - main_df['f0_data_range']).round()

                main_df['perFloorStatus'] = perFloor
                main_df['perFloor_indeed'] = np.where(main_df['relToStatus'] == 'token',
                                                      (main_df['max_token_per_power'] * perFloor).round(10),
                                                      np.where(main_df['relToStatus'] == 'data',
                                                              (main_df['max_data_per_power'] * perFloor).round(10),
                                                              (main_df['max_speaker_per_power'] * perFloor).round(10)))

                main_df['strengThresh_indeed'] = np.where(main_df['relToStatus'] == 'token',
                                                          (main_df['max_token_strength'] * strengThresh).round(8),
                                                          np.where(main_df['relToStatus'] == 'data',
                                                                  (main_df['max_data_strength'] * strengThresh).round(8),
                                                                  (main_df['max_speaker_strength'] * strengThresh).round(8)))

                main_df['periodic_fraction'] = np.where(main_df['strength_rowmax'] < main_df['strengThresh_indeed'], 0, main_df['strength_rowmax'])
                main_df['postPP'] = (main_df['total_power'] * main_df['periodic_fraction']).round(9)
                # Handling division by zero warning for log10 function
                # Calculate logPP, replacing negative or zero values with a small positive number (e.g., 1e-10)
                main_df['logPP'] = np.log10((main_df['postPP'] / main_df['perFloor_indeed'] * 10).clip(1e-10))
                main_df['logPP'] = np.where((main_df['logPP'] < 0) | main_df['logPP'].isna(), 0, main_df['logPP'])

                #main_df['logPP'] = np.log10(main_df['postPP'] / main_df['perFloor_indeed'] * 10)
                #main_df['logPP'] = np.where((main_df['logPP'] < 0) | main_df['logPP'].isna(), 0, main_df['logPP'])


                main_df['intensityRel'] = np.where(main_df['intensity'] < 0, 0, (main_df['intensity'] / main_df['intensity'].max()).round(5))
                main_df['total_powerRel'] = np.where(main_df['total_power'] < 0, 0, (main_df['total_power'] / main_df['total_power'].max()).round(5))
                main_df['postPP_rel'] = np.where(main_df['postPP'] < 0, 0, (main_df['postPP'] / main_df['postPP'].max()).round(5))
                main_df['logPP_rel'] = (main_df['logPP'] / main_df['logPP'].max()).round(5)

                import numpy as np
                from scipy import signal

                # Define the filter function
                def bwfilter(wave, f, to, n):
                    b, a = signal.butter(n, to / (f / 2), btype='low')
                    return signal.lfilter(b, a, wave)

                # Apply the 20Hz filter

                main_df['smogPP_20Hz'] = (main_df['logPP'].rolling(window=20, min_periods=1).mean() / main_df['logPP'].max()).round(5)
                main_df['smogPP_12Hz'] = (main_df['logPP'].rolling(window=12, min_periods=1).mean() / main_df['logPP'].max()).round(5)
                main_df['smogPP_8Hz'] = (main_df['logPP'].rolling(window=8, min_periods=1).mean() / main_df['logPP'].max()).round(5)
                main_df['smogPP_5Hz'] = (main_df['logPP'].rolling(window=5, min_periods=1).mean() / main_df['logPP'].max()).round(5)


                # your DataFrame for f0 interpolation and smoothing
                t_values = main_df['t'].dropna()
                f0_smooth_values = main_df['f0_smooth'].loc[main_df['t'].notna()]

                main_df['f0_interp'] = np.interp(main_df['t'], t_values, f0_smooth_values)

                #  a column 'f0_interp_stretch'
                main_df['f0_interp_stretch'] = main_df['f0_interp'].fillna(method='bfill')

                #main_df['f0_interp_stretch'] = main_df['f0_interp'].fillna(method='ffill').fillna(method='bfill')

                # Rest of the code
                main_df['f0_interp_stretch_smooth'] = main_df['f0_interp'].rolling(window=10, min_periods=1).mean().round(2).fillna(method='bfill')
                main_df['f0_interp_smooth'] = np.where(main_df['f0_interp'].notna(), main_df['f0_interp_stretch_smooth'], np.nan)

                main_df['f0_realFloorStretch'] = np.where(main_df['smogPP_20Hz'] > 0.1, main_df['f0_interp_stretch_smooth'], np.nan)
                main_df['f0_realFloorStretch'] = main_df['f0_realFloorStretch'].fillna(method='ffill')
                main_df['f0_realFloorStretch'] = np.where(
                    main_df['t'] < main_df['t'].dropna().iloc[0],
                    main_df['f0_realFloorStretch'].iloc[0],
                    main_df['f0_realFloorStretch']
                )
                # For saving the processed DataFrame to a new file
                processed_filename = f"{OutputDir}/{prefix}_processed.csv"
                main_df.to_csv(processed_filename, index=False)
                print(f"File '{filename}' processed and saved as '{processed_filename}'")
            else:
                print(f"File '{filename}' not found.")
# Example usage:
InputDir = "/content/Proper_project/data_tables/"

OutputDir = "/content/Proper_project/PerEnergy_F0Curves/"

prefixes = ['AH_1', 'DM_1', 'glenn_1', 'joe_7', 'misc_58', 'Khm_1']
data_processor = DataProcessor(InputDir, OutputDir, prefixes)
data_processor.process_data()       
