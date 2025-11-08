


import os
import json
from openai import OpenAI
import openai
import apatientreports as apr
from settings_classes import Settings
import utils
import response_formats
from datetime import datetime  

# import string 
# import random 
# import json
# from pydantic import BaseModel, Field
# import uuid
# from textwrap import dedent
# from pydantic import BaseModel
# import pandas as pd 
# import matplotlib.pyplot as plt
# print(sys.executable)


#import z_old_functions as cx
#from z_old_functions import random_id


openai_client = OpenAI()


togetherai_client = openai.OpenAI(
  api_key= os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)


os.getcwd()
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)

disorder_short = "SCZ"
disorder_long = "schizophrenia"
TEMP_WITH = "01_prompt_reports_withResponseFormat.j2"
TEMP_WITHOUT = "01_prompt_reports_withoutResponseFormat.j2"


temps = [0, 0.5, 1, 1.5 , 2]
top_ps = [0, 0.25, 0.5, 0.75, 1]
len(temps) * len(top_ps)

n_runs=100


##################################################################
##################################################################
modelmode = "openai"
os.chdir(main_dir)
directory_path = os.path.join("data/Parameters/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0
reports = []
for temp in temps:
    for top_p in top_ps:
        count += 1
        print(count, "- temp:", str(temp), "topp: ", str(top_p))
        settings_run = Settings(
        unique_name=f"{modelmode}_{disorder_short}_PARAMS_temp{temp}_topp{top_p}",
        model = "gpt-4o-mini",
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"disorder_long": disorder_long}),
        response_format = response_formats.PatientReport, 
        target_structure=response_formats.PatientReport_target_structure
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(n_runs):
            try:
                output = apr.getPatientReport_nX(
                    client=openai_client,settings=settings_run, 
                    n=1)
                end = datetime.now()
                print(end-start)
                for idx, choice in enumerate(output.choices):
                    #print(idx)
                    as_dict = choice.message.parsed.dict()
                    reports.append(choice.message.parsed)
                    json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

print("openai done.")








temps = [0, 0.25, 0.5, 0.75, 1]
top_ps = [0, 0.25, 0.5, 0.75, 1]


##################################################################
##################################################################
modelmode = "anthropic"
os.chdir(main_dir)
directory_path = os.path.join("data/Parameters/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0
reports = []
for temp in temps:
    for top_p in top_ps:
        count += 1
        print(count, "- temp:", str(temp), "topp: ", str(top_p))
        settings_run = Settings(
        unique_name=f"{modelmode}_{disorder_short}_PARAMS_temp{temp}_topp{top_p}",
        model = "claude-3-haiku-20240307",
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"disorder_long": disorder_long}),
        response_format = response_formats.response_format_tools_vPatientReport, 
        target_structure=response_formats.PatientReport_target_structure
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(n_runs):
            try:
                output = apr.getPatientReport_Anthropic(
                    settings=settings_run,tool_choice_name="patient_report")
                end = datetime.now()
                print(end-start)

                as_dict = output.content[0].input
                reports.append(as_dict)
                json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{utils.random_id()}_{idx}.json"
                utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

print("anthropic done.")






temps = [0, 0.5, 1, 1.5 , 2]
top_ps = [0, 0.25, 0.5, 0.75, 1]

##################################################################
##################################################################
modelmode = "llama"
os.chdir(main_dir)
directory_path = os.path.join("data/Parameters/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0
reports = []
for temp in temps:
    for top_p in top_ps:
        count += 1
        print(count, "- temp:", str(temp), "topp: ", str(top_p))
        settings_run = Settings(
        unique_name=f"{modelmode}_{disorder_short}_PARAMS_temp{temp}_topp{top_p}",
        model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITH, params={"disorder_long": disorder_long}),
        response_format = response_formats.PatientReport, 
        target_structure=response_formats.PatientReport_target_structure
        )
        print(settings_run)
        start = datetime.now()

        
        for idx in range(n_runs):
            try:
                output = apr.getPatientReport_Tog(
                    togetherai_client=togetherai_client,settings=settings_run, 
                    n=1)
                # settings = settings_run
                # output = togetherai_client.chat.completions.create(
    
                # model=settings.model,
                # temperature=settings.temperature,
                # top_p=settings.top_p,
                # n = 1,
                # messages=[
                #     {"role": "system","content": "You are a helpful assistant."},
                #     {"role": "user","content": settings.prompt},
                # ],
                # response_format={"type": "json_object",
                # "schema": settings.response_format.model_json_schema()}
                # )

                # print(output.choices[0].message.content)

                


                end = datetime.now()
                print(end-start)
                output.choices[0].message.content
                try: 
                    as_dict = json.loads(output.choices[0].message.content)
                    reports.append(as_dict)
                    json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
                except Exception as e:
                    print(str(e),  "Extraction did not work, save as string")
                    as_string = output.choices[0].message.content
                    reports.append(as_string)
                    json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{utils.random_id()}_{idx}_unclean.json"
                    utils.writeJSON(as_string,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

            
print("llama done.")







# Temp topp anaylsis
import pandas as pd

folder_paths = ["../MAIN/data/01_Parameters/llama",
                "../MAIN/data/01_Parameters/anthropic",
                "../MAIN/data/01_Parameters/openai"]


for folder_path in folder_paths:
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    

    data_list = []
    for idx, folder in enumerate(folders): 
        #print(idx)
        files = os.listdir(os.path.join(folder_path, folder))
        files = [file for file in files if file.endswith(".json") and  not file.endswith("settings.json")]

        for file in files: 
            with open(os.path.join(folder_path,folder,file)) as f:
                data = f.read()
            
            patient_case = data.encode("utf-8", errors="replace").decode("unicode_escape", errors="replace")
            #print(patient_case)
            unicode_chars = {}
            for char in patient_case:
                if ord(char) > 127:  # Non-ASCII characters
                    unicode_chars[str(ord(char))] = unicode_chars.get(char, 0) + 1
                    #print("found: ", repr(char))

            chars = pd.DataFrame.from_dict(unicode_chars, orient="index", columns=["count"])
            n_unicode_unique = chars.shape[0]
            n_total = sum(chars["count"])

            row = {"folder_id": folder,
                "file_id": file,
                "patient_case":patient_case.encode("utf-8", errors="replace"), 
                "n_unique":n_unicode_unique,
                "n_total":n_total, 
                }
            try:
                data = json.loads(data)
                extracted_data = {
                    "sex": data["chars"]["sex"], 
                        "age_current": data["chars"]["age_current"],
                        "age_of_onset":data["chars"]["age_of_onset"]
                        }
                
                row.update(extracted_data)
            except Exception as e:
                print(str(e))
                print("couldnt extract chars")
                extracted_data = {
                            "sex": -1, 
                        "age_current": -1,
                        "age_of_onset":-1
                        }
                row.update(extracted_data)
        
            
            data_list.append(row)
            

    bound = pd.DataFrame.from_dict(data_list, dtype="object")

    bound.to_csv(os.path.join(folder_path,"TEMP_TOPP_CHARACTERANALYSIS.csv"))


