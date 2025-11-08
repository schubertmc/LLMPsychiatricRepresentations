# 01B_retrieveData.py

import os 
import utils
from settings_classes import Settings
#import batch_patientreports as cx

# Parameters
outputfile_ending = "_structured.json"
SETTINGS_CLASS = Settings
settings_file_ending = "basesettings.json"
# Parameters


# MAIN Directory
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)
###################


# LLM 1
modelmode = "openai"
settings_files = utils.getTargetSettingFiles(f"data/06_MultReps/{modelmode}", settings_file_ending)

# Load settings, check if batch is done, write data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)

    utils.retrieveData(loaded_settings, modelmode=modelmode)

failed = []
for settings_file in settings_files:
    print(settings_file)
    try:
        loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
        utils.structureBatchData_Base(loaded_settings, modelmode, outputfile_ending=outputfile_ending)
    except:
        print("Error in structuring batch data", settings_file)
        failed.append(settings_file)

########################################################################################
########################################################################################
########################################################################################
########################################################################################


# LLM 2
os.chdir(main_dir)
# Identify setting files
modelmode = "anthropic"
settings_files = utils.getTargetSettingFiles(f"data/06_MultReps/{modelmode}", settings_file_ending)

# Load settings, check if batch is done, write data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


for settings_file in settings_files:
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structureBatchData_Base(loaded_settings, modelmode, outputfile_ending=outputfile_ending)


