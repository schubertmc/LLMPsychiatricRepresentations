#run_different_models.py


import os

import openai
from openai import OpenAI
from datetime import datetime
import apatientreports as apr
import utils

from settings_classes import Settings
import response_formats
import json
import anthropic
import data_processing

openai_client = OpenAI()

togetherai_client = openai.OpenAI(
  api_key= os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)



def basePrompt_OpenAI_NoResponseFormat(
        client,
        settings,
        n           # number of patient reports to create
        ):
    output = client.chat.completions.create(
        model=settings.model,
        temperature=settings.temperature,
        top_p=settings.top_p,
        n = n,
        messages =  [{"role": "user", "content": settings.prompt}],
    )
    return output


def basePrompt_Anthropic_NoResponseFormat(
        settings,
        ):
    output = anthropic.Anthropic().messages.create(
    model=settings.model,
    max_tokens=1024,
    temperature=settings.temperature,
    top_p=settings.top_p,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": settings.prompt, 
                }
            ]
        }
    ],
    )
    return output 




def basePrompt_Llama_Tog(
        togetherai_client,
        settings
        ):

    output = togetherai_client.chat.completions.create(
    model=settings.model,
    temperature=settings.temperature,
    top_p=settings.top_p,
    n = 1,
    messages=[
        {"role": "user","content": settings.prompt},
    ]
    )
    return output



def extractStructure_OpenAI(
        client,
        input_raw,
        response_format
        ):
    output = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=1,
        top_p=1,
        n = 1,
        response_format = response_format,
        messages =  [{"role": "user", "content":f"Please extract the structured data from the following text: {input_raw}"}],
    )
    return output



os.getcwd()
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)

disorder_short = "SCZ"
disorder_long = "schizophrenia"
TEMP_WITH = "01_prompt_reports_withResponseFormat.j2"
TEMP_WITHOUT = "01_prompt_reports_withoutResponseFormat.j2"
n_runs=100
temp = 1
top_p = 1









##################################################################
##################################################################
modelmode = "openai"
os.chdir(main_dir)
directory_path = os.path.join("data/DifferentModels/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)

prompt_for_raw = utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITH, params={"disorder_long": disorder_long})




models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "o1-preview", "o1-mini"]
models = [ "o1-preview", "o1-mini"] # gpt 4o and 4o mini were not run with the basePrompt task but with the drirect structured output



count = 0
for i, cur_model in enumerate(models):
        count += 1
        settings_run = Settings(
        unique_name=f"{cur_model}_{disorder_short}_model_{i}",
        model = cur_model,
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= prompt_for_raw,
        response_format = None, 
        target_structure=None
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(100):
            try:
                output = basePrompt_OpenAI_NoResponseFormat(
                    settings=settings_run, 
                    n=1)
                end = datetime.now()
                print(end-start)
                for idx, choice in enumerate(output.choices):
                    #print(idx)
                    raw = choice.message.content
                    json_filename = f"{settings_run.unique_name}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(raw,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

print("openai done.")







modelmode = "anthropic"
os.chdir(main_dir)
directory_path = os.path.join("data/DifferentModels/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)


models= ["claude-3-haiku-20240307", 
         "claude-3-sonnet-20240229"]


count = 0
for i, cur_model in enumerate(models):
        count += 1
        settings_run = Settings(
        unique_name=f"{cur_model}_{disorder_short}_model_{i}",
        model = cur_model,
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= prompt_for_raw,
        response_format = None, 
        target_structure=None
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(100):
            try:
                output = basePrompt_Anthropic_NoResponseFormat(
                    settings=settings_run)
                end = datetime.now()
                print(end-start)
                for idx, choice in enumerate(output.content):
                    #print(idx)
                    raw = choice.text
                    json_filename = f"{settings_run.unique_name}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(raw,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

print("anthropic done.")



modelmode = "llama"
os.chdir(main_dir)
directory_path = os.path.join("data/DifferentModels/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)


models = [
	"Meta-Llama-3.1-8B-Instruct-Turbo",
	"Meta-Llama-3.1-70B-Instruct-Turbo",
	"Meta-Llama-3.1-405B-Instruct-Turbo"
]


count = 0
for i, cur_model in enumerate(models):
        count += 1
        settings_run = Settings(
        unique_name=f"{cur_model}_{disorder_short}_model_{i}",
        model = "meta-llama/"+ cur_model,
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= prompt_for_raw,
        response_format = None, 
        target_structure=None
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(100):
            try:
                output = basePrompt_Llama_Tog(
                     togetherai_client=togetherai_client,
                    settings=settings_run)
                end = datetime.now()
                print(end-start)
                for idx, choice in enumerate(output.choices):
                    #print(idx)
                    raw = choice.message.content
                    json_filename = f"{settings_run.unique_name}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(raw,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

print("llama done.")




### Extract structured information from the raw data


base_folder= "../MAIN/data/DifferentModels/"
os.chdir(base_folder)

modelmodes = ["openai", "anthropic", "llama"]

for modelmode in modelmodes:
    directory_path = os.path.join(base_folder, modelmode)
    os.chdir(directory_path)
    models = os.listdir(directory_path)
    models =[model for model in models if not model.endswith(".DS_Store")]
    for model in models:
        for idx, file in enumerate(os.listdir(os.path.join(directory_path, model))):
            print(file)
            if not file.endswith("settings.json"):
                with open(os.path.join(directory_path, model, file), "r") as f:
                    raw = json.load(f)
                
                output = extractStructure_OpenAI(
                    client=openai_client,
                    input_raw=raw,
                    response_format=response_formats.PatientReport
                )
                structured = output.choices[0].message.parsed.dict()
                
                json_filename = f"{file}_extract.json"
                model_stru = model + "_structured"
                os.makedirs(os.path.join(directory_path, model_stru), exist_ok=True)
                utils.writeJSON(structured, os.path.join(directory_path, model_stru, json_filename))
    
    print(f"{modelmode} done.")






### 
#data_processing.bindReportsFromFolder()

modelmodes = ["openai", "anthropic", "llama"]

base_folder= "../MAIN/data/DifferentModels/"
os.chdir(base_folder)


dfs = []
for modelmode in modelmodes:
	directory_path = os.path.join(base_folder, modelmode)
	os.chdir(directory_path)
	models = os.listdir(directory_path)
	models =[model for model in models if model.endswith("_structured")]
	for model in models:
		path = os.path.join(directory_path, model)
		data = data_processing.bindReportsFromFolder(path)
		data["model"] = model
		dfs.append(data)
	print(f"{modelmode} done.")
import pandas as pd

bound = pd.concat(dfs)
bound.to_csv(os.path.join(base_folder, "different_models.csv"))


