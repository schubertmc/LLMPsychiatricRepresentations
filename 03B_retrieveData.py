# 01B_retrieveData.py

import os 
import utils
from settings_classes import DetailsSettings
#import batch_patientreports as cx




# Parameters
field_name = "PHQ9"
originalfile_ending = "_structured_withDetails.json"
outputfile_ending = "_structured_withDetails_V2.json"
SETTINGS_CLASS = DetailsSettings
settings_file_ending = "PHQ9_detailssettings.json"
# Parameters


# MAIN Directory
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)
###################


# LLM 1
modelmode = "openai"
settings_files = utils.getTargetSettingFiles(f"data/PatientDatasets/{modelmode}", settings_file_ending)

# Retrieve data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


# Process data
for settings_file in settings_files:
    print(settings_file)
    # Load the settings
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending=outputfile_ending, originalfile_ending=originalfile_ending, field_name=field_name)
   


########################################################################################################


# LLM 2
os.chdir(main_dir)
modelmode = "anthropic"
settings_files = utils.getTargetSettingFiles(f"data/PatientDatasets/{modelmode}", settings_file_ending)


# Retrieve data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


# Process data
for settings_file in settings_files:
    print(settings_file)
    # Load the settings
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending=outputfile_ending, originalfile_ending=originalfile_ending, field_name=field_name)
   





########################################################################################################

# LLM 3
os.chdir(main_dir)
modelmode = "llama"
settings_files = utils.getTargetSettingFiles(f"data/PatientDatasets/{modelmode}", settings_file_ending)

# Retrieve data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


# Process data
for settings_file in settings_files:
    print(settings_file)
    # Load the settings
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending=outputfile_ending, originalfile_ending=originalfile_ending, field_name=field_name)
   




########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################

field_name = "PANSS"
originalfile_ending = "_structured_withDetails.json"
outputfile_ending = "_structured_withDetails_V2.json"
SETTINGS_CLASS = DetailsSettings
settings_file_ending = "PANSS_detailssettings.json"


# MAIN Directory
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)
###################

# LLM 1
modelmode = "openai"
settings_files = utils.getTargetSettingFiles(f"data/PatientDatasets/{modelmode}", settings_file_ending)

# Retrieve data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


# Process data
for settings_file in settings_files:
    print(settings_file)
    # Load the settings
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending=outputfile_ending, originalfile_ending=originalfile_ending, field_name=field_name)
   


########################################################################################################


# LLM 2
os.chdir(main_dir)
modelmode = "anthropic"
settings_files = utils.getTargetSettingFiles(f"data/PatientDatasets/{modelmode}", settings_file_ending)


# Retrieve data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


# Process data
for settings_file in settings_files:
    print(settings_file)
    # Load the settings
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending=outputfile_ending, originalfile_ending=originalfile_ending, field_name=field_name)
   



########################################################################################################


# LLM 3
os.chdir(main_dir)
modelmode = "llama"
settings_files = utils.getTargetSettingFiles(f"data/PatientDatasets/{modelmode}", settings_file_ending)

# Retrieve data
for settings_file in settings_files:
    # Load the settings
    print(settings_file)
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.retrieveData(loaded_settings, modelmode=modelmode)


# Process data
for settings_file in settings_files:
    print(settings_file)
    # Load the settings
    loaded_settings = SETTINGS_CLASS.load_settings(settings_file)
    utils.structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending=outputfile_ending, originalfile_ending=originalfile_ending, field_name=field_name)
   
