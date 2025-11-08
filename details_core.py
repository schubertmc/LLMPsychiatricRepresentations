#02_runDetails_Batch.py

import os
import json 
from datetime import datetime


import settings_classes
import batch_patientreports as cx
import apatientreports as apr
import response_formats
import utils

from data_processing import summarizePatientData
from openai.lib._pydantic import to_strict_json_schema # type: ignore
from openai.lib._parsing._completions import type_to_response_format_param # type: ignore

# MAIN Directory
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")

os.chdir(main_dir)
os.chdir("code")

# ##GENERAL PARAMS
# field_name="details"
# response_format_PYDANTIC =response_formats.Details
# response_format_TOOLS = response_formats.response_format_tools_vPatientDetails
# target_structure_GEN = response_formats.Details_target_structure
# tool_choice_name="patient_details"
# TEMP_WITH = "02_prompt_details_withResponseFormat.j2"
# TEMP_WITHOUT = "02_prompt_details_withoutResponseFormat.j2"
# base_path = "../data/PatientDatasets_EXXATESTING/"
#information_file = "structured.json"
# ##GENERAL PARAMS


def run_details_main(configs, filter = None):
    field_name = configs["field_name"]
    response_format_PYDANTIC = configs["response_format_PYDANTIC"]
    response_format_TOOLS = configs["response_format_TOOLS"]
    target_structure_GEN = configs["target_structure_GEN"]
    tool_choice_name = configs["tool_choice_name"]
    TEMP_WITH = configs["TEMP_WITH"]
    TEMP_WITHOUT = configs["TEMP_WITHOUT"]
    information_file = configs["information_file"] 
    base_path = configs["base_path"]

    #LLM 1
    modelmode = "openai"
    folder_path = os.path.join(base_path, modelmode)
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    if filter is not None:
        folders = [folder for folder in folders if folder.count(filter)>0] # filter for folder that contain eg MDD 

    for folder in folders:
        print(folder)
        current_path = os.path.join(folder_path, folder)
        os.chdir(current_path)
        files = os.listdir(current_path)
        settings_file = [file for file in files if file.count("basesettings.json")>0][0]

        original_settings = json.load(open(settings_file))
        details_settings = settings_classes.DetailsSettings(
            unique_name=f"{original_settings['unique_name']}_{field_name}",
            model = original_settings["model"],
            temperature=1,
            top_p=1,
            prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"": ""}),
            response_format = response_format_PYDANTIC,
            target_structure=target_structure_GEN,
            directory_path=original_settings["directory_path"],
            field_name = field_name
        )

        cx.create_details_batchfiles(details_settings=   details_settings,
                                    original_settings=original_settings, 
                                    field=field_name, 
                                    mode=modelmode, 
                                    tool_choice_name=tool_choice_name,

                                    information_file=information_file)
        

        batch_id = cx.sendAndStartBatchFile(current_path, f"BatchReqs_{details_settings.unique_name}.jsonl", mode=modelmode)
        details_settings.batch_id = batch_id
        details_settings.save_settings()






    #LLM 2

    modelmode = "anthropic"
    folder_path = os.path.join(base_path, modelmode)
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    if filter is not None:
        folders = [folder for folder in folders if folder.count(filter)>0] # filter for folder that contain eg MDD 

    for folder in folders:
        print(folder)
        current_path = os.path.join(folder_path, folder)
        os.chdir(current_path)
        files = os.listdir(current_path)
        settings_file = [file for file in files if file.count("basesettings.json")>0][0]

        original_settings = json.load(open(settings_file))
        details_settings = settings_classes.DetailsSettings(
            unique_name=f"{original_settings['unique_name']}_{field_name}",
            model = original_settings["model"],
            temperature=1,
            top_p=1,
            prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"": ""}) + "Ensure that all fields are filled. Do not use placeholders such as <UNKNOWN> or null",
            response_format = response_format_TOOLS, 
            target_structure=target_structure_GEN,
            directory_path=original_settings["directory_path"],
            field_name = field_name


        )

        cx.create_details_batchfiles(details_settings=   details_settings,
                                    original_settings=original_settings, 
                                    field=field_name, 
                                    mode=modelmode, 
                                    tool_choice_name=tool_choice_name,
                                    information_file=information_file)
        

        batch_id = cx.sendAndStartBatchFile(current_path, f"BatchReqs_{details_settings.unique_name}.jsonl", mode=modelmode)
        details_settings.batch_id = batch_id
        details_settings.save_settings()



    # LLM 3
    modelmode = "llama"
    folder_path = os.path.join(base_path, modelmode)
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    if filter is not None:
            folders = [folder for folder in folders if folder.count(filter)>0] # filter for folder that contain eg MDD
    for folder in folders: 
        print(folder)
        current_path = os.path.join(folder_path, folder)
        os.chdir(current_path)
        files = os.listdir(current_path)
        settings_file = [file for file in files if file.count("basesettings.json")>0][0]

        original_settings = json.load(open(settings_file))
        details_settings = settings_classes.DetailsSettings(
            unique_name=f"{original_settings['unique_name']}_{field_name}",
            model = original_settings["model"],
            temperature=1,
            top_p=1,
            prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITH, params={"": ""}) + " Ensure that all fields are filled. Do not use placeholders such as <UNKNOWN> or null.",
            response_format = response_format_PYDANTIC, 
            target_structure=target_structure_GEN,
            directory_path=original_settings["directory_path"],
            field_name = field_name
        )

        cx.create_details_batchfiles(details_settings=details_settings,
                                    original_settings=original_settings, 
                                    field=field_name, 
                                    mode=modelmode,
                                    tool_choice_name=tool_choice_name,
                                    information_file=information_file)
         

        batch_id = cx.sendAndStartBatchFile(current_path, f"BatchReqs_{details_settings.unique_name}.jsonl", mode=modelmode, parallel_mode=True)
        details_settings.batch_id = batch_id
        details_settings.save_settings()


       ##apr.run_details(details_settings, original_settings, current_path, field=field_name, mode=modelmode, tool_choice_name=tool_choice_name)


    print("Done.")
