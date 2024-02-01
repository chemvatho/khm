import os

class DirectoryCreator:
    def __init__(self, InDirAudio, OutDirIntensityTier, OutDirPitchObject, OutDirPitchTier, OutDirTextGrid, OutDirDatatable, OutDirOutput_csv):
        self.InDirAudio = InDirAudio
        self.OutDirIntensityTier = OutDirIntensityTier
        self.OutDirPitchObject = OutDirPitchObject
        self.OutDirPitchTier = OutDirPitchTier
        self.OutDirTextGrid = OutDirTextGrid
        self.OutDirDatatable = OutDirDatatable
        self.OutDirOutput_csv = OutDirOutput_csv

    def create_directories(self):
        directories = [
            self.InDirAudio,
            self.OutDirIntensityTier,
            self.OutDirPitchObject,
            self.OutDirPitchTier,
            self.OutDirTextGrid,
            self.OutDirDatatable,
            self.OutDirOutput_csv
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Directory created: {directory}")
            else:
                print(f"Directory already exists: {directory}")

# Usage example
if __name__ == "__main__":
    InDirAudio = "/content/Proper_project/praat_data/audio/"
    OutDirIntensityTier = "/content/Proper_project/praat_data/intensity_tiers/"
    OutDirPitchObject = "/content/Proper_project/praat_data/pitch_objects/"
    OutDirPitchTier = "/content/Proper_project/praat_data/pitch_tiers/"
    OutDirTextGrid = "/content/Proper_project/praat_data/textgrid/"
    OutDirDatatable = "/content/Proper_project/data_tables/"
    OutDirOutput_csv = "/content/Proper_project/output_csv/"

    dir_creator = DirectoryCreator(
        InDirAudio, OutDirIntensityTier, OutDirPitchObject, OutDirPitchTier,
        OutDirTextGrid, OutDirDatatable, OutDirOutput_csv
    )
    dir_creator.create_directories()
