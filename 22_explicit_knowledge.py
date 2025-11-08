
# Explicit knowledge comparison 

import os
from settings_classes import Settings
import response_formats
import utils

import apatientreports as apr
import openai
import json


import os

import openai
from openai import OpenAI
from datetime import datetime
import apatientreports as apr
import utils

from settings_classes import Settings
import response_formats
import json



togetherai_client = openai.OpenAI(
  api_key= os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)

#MAIN Directory
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)

##GENERAL PARAMS
# anthropic settings:

response_format_PYDANTIC =response_formats.Stats
response_format_TOOLS = response_formats.response_format_tools_Stats
target_structure_GEN = response_formats.Stats_target_structure
TEMP_WITH = "07_explicitknowledge_withResponseFormat.j2"
TEMP_WITHOUT = "07_explicitknowledge_withoutResponseFormat.j2"
##GENERAL PARAMS

# dictionary of all the disorders
disorder_dict = {
   "MDD": "major depressive disorder",
   "SCZ": "schizophrenia",
   "ADHD": "attention-deficit hyperactivity disorder",
    "AUT": "autism spectrum disorder",
    "CD": "conduct disorder",
   "ED": "eating disorder",
    "ANX": "anxiety disorder",
    "BIP": "bipolar disorder",
}


##################################################################
##################################################################

modelmode = "openai"
os.chdir(main_dir)
directory_path = os.path.join("data/07_Explicit/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0
for disorder_short, disorder_long in disorder_dict.items():
        count += 1
        settings_run = Settings(
        unique_name=f"{modelmode}_{disorder_short}_expl",
        model = "gpt-4o-mini",
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=1,
        top_p=1,
        prompt=utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"disorder_long": disorder_long}) ,
        response_format = response_format_PYDANTIC, 
        target_structure=target_structure_GEN
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(1):
            try:
                output = apr.getPatientReport_nX(
                    client=openai,settings=settings_run, 
                    n=100)
                end = datetime.now()
                print(end-start)
                for idx, choice in enumerate(output.choices):
                    #print(idx)
                    as_dict = choice.message.parsed.dict()
                    json_filename = f"{settings_run.prompt}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(str(e))
                print("didnt work")

print("openai done.")





##### # Excecute below to generate summary file  #############
import os
import data_processing
import pandas as pd


main_dir = "../MAIN/"

modelmodes = ["openai"]
base_folder= os.path.join(main_dir,"data/07_Explicit")
os.chdir(base_folder)


dfs = []
for modelmode in modelmodes:
    directory_path = os.path.join(base_folder, modelmode)
    os.chdir(directory_path)
    expl_files = os.listdir(directory_path)
    expl_files = [f for f in expl_files if not f.endswith(".DS_Store")]
    for expl_file in expl_files:
        path = os.path.join(directory_path, expl_file)
        files = os.listdir(path)
        files = [f for f in files if not f.endswith(".DS_Store")]
        for file in files:
            file_path = os.path.join(directory_path, expl_file, file)
            print(file_path)
            if file_path.endswith(".json") and not file_path.endswith("settings.json"):
                # read in json file
                data = json.load(open(file_path, 'r'))
                data["modelmode"] = modelmode
                data["disorder"] = expl_file
                print(f"{modelmode} done.")
                dfs.append(pd.DataFrame([data]))

bound = pd.concat(dfs)
bound.to_csv(os.path.join(base_folder, "explicit_information.csv"))


print("Done")


####
