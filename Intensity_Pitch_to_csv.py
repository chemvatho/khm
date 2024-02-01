import os
import re
import pandas as pd
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self, audio_directory, intensity_directory, pitch_directory):
        self.audio_directory = audio_directory
        self.intensity_directory = intensity_directory
        self.pitch_directory = pitch_directory

    def get_full_time_table(self):
        data = []

        for root, dirs, files in os.walk(self.audio_directory):
            for filename in files:
                if filename.endswith(".wav"):
                    file_path = os.path.join(root, filename)
                    filename_bits = re.match(r"^(.*?)_([^_]*?)\.wav$", filename)
                    if filename_bits:
                        speaker = filename_bits.group(1)

                        it = AudioSegment.from_file(file_path)
                        tmin = 1  # Start from 1 millisecond
                        tmax = it.duration_seconds * 1000  # Convert duration to milliseconds
                        time = list(range(int(tmin), int(tmax) + 1))

                        for t in time:
                            data.append({
                                'file': filename.replace(".wav", ""),  # Remove .wav extension
                                't': t,
                                'speaker': speaker,
                            })

        fullTime_df = pd.DataFrame(data)
        return fullTime_df

    def extract_intensity_data_from_praat_intensity_tier(self, intensity_tier_path):
        data = []

        with open(intensity_tier_path, 'r') as f:
            lines = f.readlines()
            duration = None

            for line in lines:
                line = line.strip()
                if line.startswith("File type"):
                    continue  # Skip header lines

                if duration is None:
                    duration = int(float(line) * 1000)  # Convert duration from seconds to ms and remove decimal points
                else:
                    intensity = float(line)
                    data.append({
                        'file': os.path.splitext(os.path.basename(intensity_tier_path))[0],
                        't': duration,
                        'intensity': intensity
                    })
                    duration = None

        return pd.DataFrame(data)

    def get_intensity_data(self):
        data = []

        for root, dirs, files in os.walk(self.intensity_directory):
            for filename in files:
                if filename.endswith(".IntensityTier"):
                    file_path = os.path.join(root, filename)

                    intensity_df = self.extract_intensity_data_from_praat_intensity_tier(file_path)
                    data.append(intensity_df)

        if data:
            result_df = pd.concat(data, ignore_index=True)
            return result_df
        else:
            return None

    def extract_f0_smooth_data_from_praat_pitch_tier(self, pitch_tier_path):
        data = []

        with open(pitch_tier_path, 'r') as f:
            lines = f.readlines()
            duration = None

            for line in lines:
                line = line.strip()
                if line.startswith("File type"):
                    continue  # Skip header lines

                if duration is None:
                    duration = int(float(line) * 1000)  # Convert duration from seconds to ms and remove decimal points from time
                else:
                    f0_smooth = float(line)
                    data.append({
                        'file': os.path.splitext(os.path.basename(pitch_tier_path))[0],
                        't': duration,
                        'f0_smooth': f0_smooth
                    })
                    duration = None

        return pd.DataFrame(data)

    def get_f0_smooth_data(self):
        data = []

        for root, dirs, files in os.walk(self.pitch_directory):
            for filename in files:
                if filename.endswith(".PitchTier"):
                    file_path = os.path.join(root, filename)

                    f0_smooth_df = self.extract_f0_smooth_data_from_praat_pitch_tier(file_path)
                    data.append(f0_smooth_df)

        if data:
            result_df = pd.concat(data, ignore_index=True)
            return result_df
        else:
            return None

    def process_audio_files(self):
        fullTime_df = self.get_full_time_table()
        intensity_df = self.get_intensity_data()
        f0_smooth_df = self.get_f0_smooth_data()

        return fullTime_df, intensity_df, f0_smooth_df

    def save_to_csv_by_file(self, fullTime_df, intensity_df, f0_smooth_df):

        if fullTime_df is not None:
            unique_files = fullTime_df['file'].unique()

            for file in unique_files:
                file_fullTime_df = fullTime_df[fullTime_df['file'] == file]
                csv_filename_fullTime = f"/content/Proper_project/data_tables/{file}_fullTime_data.csv"
                file_fullTime_df.to_csv(csv_filename_fullTime, index=False)
                print(f"Full time data for '{file}' saved to {csv_filename_fullTime}")

        if intensity_df is not None:
            unique_files = intensity_df['file'].unique()

            for file in unique_files:
                file_intensity_df = intensity_df[intensity_df['file'] == file]
                csv_filename_intensity = f"/content/Proper_project/data_tables/{file}_intensity_data.csv"
                file_intensity_df.to_csv(csv_filename_intensity, index=False)
                print(f"Intensity data for '{file}' saved to {csv_filename_intensity}")

        if f0_smooth_df is not None:
            unique_files = f0_smooth_df['file'].unique()

            for file in unique_files:
                file_f0_smooth_df = f0_smooth_df[f0_smooth_df['file'] == file]
                csv_filename_f0_smooth = f"/content/Proper_project/data_tables/{file}_f0_smooth_data.csv"
                file_f0_smooth_df.to_csv(csv_filename_f0_smooth, index=False)
                print(f"F0 smooth data for '{file}' saved to {csv_filename_f0_smooth}")

        print("Data saved to CSV files conditioned by audio file name.")

    # Rest of the existing AudioProcessor class remains unchanged...

# Example usage
audio_directory = "/content/Proper_project/praat_data/audio"
intensity_directory = "/content/Proper_project/praat_data/intensity_tiers/"
pitch_directory = "/content/Proper_project/praat_data/pitch_tiers/"

processor = AudioProcessor(audio_directory, intensity_directory, pitch_directory)
fullTime_df, intensity_df, f0_smooth_df = processor.process_audio_files()
processor.save_to_csv_by_file(fullTime_df, intensity_df, f0_smooth_df)