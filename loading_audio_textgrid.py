import glob
import os

class AudioTextgridLoader:
    def __init__(self, audio_dir, textgrid_dir):
        self.audio_files = glob.glob(audio_dir + "/*.wav")
        self.textgrid_files = glob.glob(textgrid_dir + "/*.TextGrid")
        self.loaded_audio_prefixes = self.load_audio_files_with_prefixes()

    def read_textgrid(self, file_path):
        with open(file_path, 'r', encoding='latin-1') as file:
            textgrid_content = file.read()
        return textgrid_content

    def load_audio_files_with_prefixes(self):
        audio_prefixes = {}
        for i, audio_file in enumerate(self.audio_files):
            name_prefix = os.path.basename(audio_file).replace(".wav", "")
            matching_textgrid = [textgrid for textgrid in self.textgrid_files if name_prefix in textgrid]

            if matching_textgrid:
                textgrid_content = self.read_textgrid(matching_textgrid[0])  # Assuming only one matching TextGrid file
                audio_prefixes[audio_file] = {
                    'prefix': name_prefix,
                    'textgrid_content': textgrid_content
                }
        return audio_prefixes

    def print_loaded_audio_prefixes(self):
        for audio_file, info in self.loaded_audio_prefixes.items():
            print(f"Audio File: {audio_file}")
            print(f"Name Prefix: {info['prefix']}")
            # Uncomment the line below if you want to print TextGrid content
            # print(f"Matching TextGrid content:\n{info['textgrid_content']}")
            print("--------------------------------------------")

# Example usage:
audio_dir_path = "/content/drive/MyDrive/Proper_project/praat_data/audio"
textgrid_dir_path = "/content/drive/MyDrive/Proper_project/praat_data/textgrid"


