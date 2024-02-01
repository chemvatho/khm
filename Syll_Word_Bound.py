import os
import pandas as pd
from praatio import tgio

class TextGridProcessor:
    def __init__(self, textgrid_directory, output_directory):
        self.textgrid_directory = textgrid_directory
        self.output_directory = output_directory
        self.textGridSyll_data = {}
        self.textGridWord_data = {}

    def process_textgrid_file_syllable(self, file_path):
        filename = os.path.splitext(os.path.basename(file_path))[0]
        tg = tgio.openTextgrid(file_path)

        syll_tier = tg.tierDict.get("Syllable")
        if syll_tier is None:
            return

        syll_intervals = syll_tier.entryList
        syll_data = []

        print(f"File: {filename} - Syllable Intervals:")
        for interval in syll_intervals:
            start_time = int(interval[0] * 1000)
            end_time = int(interval[1] * 1000)
            mid_time = (start_time + end_time) // 2
            label = interval[2]

            print(f"Start: {start_time}, End: {end_time}, Label: '{label}'")

            if label != "":
                syll_data.append({
                    "file": filename,
                    "t": start_time,
                    "syll_start": start_time,
                    "syll_mid": mid_time,
                    "syll_end": end_time,
                    "syll_bounds": start_time,
                    "syll_label": label
                })

        self.textGridSyll_data[filename] = syll_data

    def process_textgrid_file_word(self, file_path):
        filename = os.path.splitext(os.path.basename(file_path))[0]
        tg = tgio.openTextgrid(file_path)

        word_tier = tg.tierDict.get("Word")
        if word_tier is None:
            return

        word_intervals = word_tier.entryList
        word_data = []

        print(f"File: {filename} - Word Intervals:")
        for interval in word_intervals:
            start_time = int(interval[0] * 1000)
            end_time = int(interval[1] * 1000)
            mid_time = (start_time + end_time) // 2
            label = interval[2]

            print(f"Start: {start_time}, End: {end_time}, Label: '{label}'")

            if label != "":
                word_data.append({
                    "file": filename,
                    "t": start_time,
                    "word_start": start_time,
                    "word_mid": mid_time,
                    "word_end": end_time,
                    "word_bounds": start_time,
                    "word_label": label
                })

        self.textGridWord_data[filename] = word_data

    def process_textgrid_files(self):
        files_textGrid_syllable = [os.path.join(self.textgrid_directory, file) for file in os.listdir(self.textgrid_directory) if file.endswith(".TextGrid")]
        for file_path in files_textGrid_syllable:
            self.process_textgrid_file_syllable(file_path)

        files_textGrid_word = [os.path.join(self.textgrid_directory, file) for file in os.listdir(self.textgrid_directory) if file.endswith(".TextGrid")]
        for file_path in files_textGrid_word:
            self.process_textgrid_file_word(file_path)

    def convert_to_dataframes(self):
        for filename, data in self.textGridSyll_data.items():
            syll_df = pd.DataFrame(data)
            syll_df = syll_df.dropna()
            syll_df["syll_bounds"] = syll_df.apply(lambda row: row["syll_end"] if pd.isna(row["syll_bounds"]) else row["syll_bounds"], axis=1)
            self.textGridSyll_data[filename] = syll_df

        for filename, data in self.textGridWord_data.items():
            word_df = pd.DataFrame(data)
            word_df = word_df.dropna(subset=["t"])
            word_df["word_bounds"] = word_df.apply(lambda row: row["word_end"] if pd.isna(row["word_bounds"]) and not pd.isna(word_df.iloc[row.name - 1]["word_end"]) else row["word_bounds"], axis=1)
            self.textGridWord_data[filename] = word_df

    def save_to_csv(self):
        for filename, syll_df in self.textGridSyll_data.items():
            output_path_syllable = os.path.join(self.output_directory, f"{filename}_syllable_data.csv")
            syll_df.to_csv(output_path_syllable, index=False)
            print(f"Syllable DataFrame saved to CSV: {output_path_syllable}")

        for filename, word_df in self.textGridWord_data.items():
            output_path_word = os.path.join(self.output_directory, f"{filename}_word_data.csv")
            word_df.to_csv(output_path_word, index=False)
            print(f"Word DataFrame saved to CSV: {output_path_word}")

# Usage example:
textgrid_processor = TextGridProcessor(
    "/content/Proper_project/praat_data/textgrids/",
    "/content/Proper_project/data_tables/"
)

textgrid_processor.process_textgrid_files()
textgrid_processor.convert_to_dataframes()
textgrid_processor.save_to_csv()
