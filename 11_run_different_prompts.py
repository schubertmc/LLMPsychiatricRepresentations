


import os

import openai
from openai import OpenAI
from datetime import datetime
import apatientreports as apr
import utils

from settings_classes import Settings
import response_formats
import json
import data_processing
import pandas as pd




os.chdir("../MAIN/data/02_Prompts")



# Run different prompts
prompts = ["Please create a short patient report for a patient with schizophrenia.",
"Please provide a brief patient report for a case with schizophrenia.",  
"Create a short clinical summary for a patient diagnosed with schizophrenia.",  
"Generate a concise patient report for a person presenting with schizophrenia.",  
"Write a quick patient note describing a case of schizophrenia.",  
"Summarize a patient’s presentation and history with schizophrenia in a short report.",  
"Draft a brief clinical report focusing on a patient with schizophrenia.",  
"Please prepare a concise patient case summary for a diagnosis of schizophrenia.",  
"Compose a short report outlining the clinical features of a patient with schizophrenia.",  
"Create a brief clinical description for a patient case involving schizophrenia.",  
"Provide a succinct patient summary focusing on the diagnosis of schizophrenia.",  
"Develop a short patient case report highlighting a diagnosis of schizophrenia.",  
"Write a short patient case report for an individual with schizophrenia.",  
"Summarize the clinical presentation and key findings for a patient diagnosed with schizophrenia.",  
"Compose a brief clinical summary for a patient presenting with symptoms of schizophrenia.",  
"Generate a concise report focusing on the diagnostic criteria and findings of schizophrenia.",  
"Write a short clinical vignette describing a case of schizophrenia.",  
"Create a brief case report detailing a patient’s history and presentation with schizophrenia.",  
"Prepare a short patient summary focusing on the clinical presentation and course of schizophrenia.", 
"Develop a succinct patient report that highlights the management and outcome of schizophrenia."
]



openai_client = OpenAI()


togetherai_client = openai.OpenAI(
  api_key= os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)


os.getcwd()
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts/")
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

# prompts = ["Please create a short patient report for a patient with schizophrenia.",
#         "Please create a detailed patient report for a patient with schizophrenia, accounting for variance in symptoms, demographics, and treatment responses. Consider real-world case variability.", 
#         "Please create a short patient report for a patient with schizophrenia. Please consider that each variable has a specific variance.",
#         "Please sample a short patient report for a patient with schizophrenia from the real distribution of patient reports. Consider the variance in symptoms, and demographics.",
#         "Please simulate a patient report for schizophrenia by sampling from real-world distributions. Reflect statistical variances observed in clinical studies.",
#         "Write a patient report for schizophrenia, ensuring each variable represents the variance typically observed in clinical populations.",
#            ]

import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")
# basic chat test 
response = openai_client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Please create a short patient report for a patient with schizophrenia."}
    ],
    temperature=1
)
print(response.choices[0].message.content)



modelmode = "openai"
os.chdir(main_dir)
directory_path = os.path.join("data/02_Prompts/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0
for idx, prompt in enumerate(prompts):
        count += 1
        print(count, "- temp:", str(temp), "topp: ", str(top_p))
        settings_run = Settings(
        unique_name=f"{modelmode}_{disorder_short}_prompt_{idx}",
        model = "gpt-4o-mini",
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= prompt,
        response_format = response_formats.PatientReport, 
        target_structure=response_formats.PatientReport_target_structure
        )
        print(settings_run)
        start = datetime.now()

        for idx in range(1):
            try:
                output = apr.getPatientReport_nX(
                    client=openai_client,settings=settings_run, 
                    n=100)
                end = datetime.now()
                print(end-start)
                for idx, choice in enumerate(output.choices):
                    #print(idx)
                    as_dict = choice.message.parsed.dict()
                    json_filename = f"{settings_run.prompt}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

print("openai done.")




##################################################################
##################################################################
modelmode = "anthropic"
os.chdir(main_dir)
directory_path = os.path.join("data/02_Prompts/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0

for idx, prompt in enumerate(prompts):
    count += 1
    # only run from idx 11 onwards
    if idx < 11:
        continue
    print(count, "- temp:", str(temp), "topp: ", str(top_p))
    settings_run = Settings(
    unique_name=f"{modelmode}_{disorder_short}_prompt_{idx}",
    model = "claude-3-haiku-20240307",
    diagnosis_long=disorder_long,
    diagnosis_short=disorder_short,
    temperature=temp,
    top_p=top_p,
    prompt= prompt,
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
            json_filename = f"{settings_run.prompt}_{utils.random_id()}_{idx}.json"
            utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
        except Exception as e: 
            print(idx)
            print(str(e))
            print("didnt work")

print("anthropic done.")


##################################################################
##################################################################
modelmode = "llama"
os.chdir(main_dir)
directory_path = os.path.join("data/02_Prompts/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path)
count = 0
import time
for idx, prompt in enumerate(prompts):
        prompt_filename  = prompt
        time.sleep(1)
        count += 1
        print(count, "- temp:", str(temp), "topp: ", str(top_p))
        print(prompt)
        settings_run = Settings(
        unique_name=f"{modelmode}_{disorder_short}_prompt_{idx}",
        model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", 
        diagnosis_long=disorder_long,
        diagnosis_short=disorder_short,
        temperature=temp,
        top_p=top_p,
        prompt= prompt + """\nPlease only return your answer in JSON format, following the structure below: 
{
    "patient_report": "<Patient report>",
    "chars": {
        "sex": "<str> ["Male", "Female"]",
        "age_current": <int> (Current age),
        "age_of_onset": <int> (Age of onset)   
    } 
}\n
""", 
        response_format = response_formats.PatientReport, 
        target_structure=response_formats.PatientReport_target_structure
        )
        #print(settings_run)
        start = datetime.now()
        
        for idx in range(n_runs):
            try:
                output = apr.getPatientReport_Tog(
                   togetherai_client=togetherai_client,settings=settings_run, 
                   n=1)

                end = datetime.now()
                print(end-start)
                output.choices[0].message.content
                try: 
                    as_dict = json.loads(output.choices[0].message.content)
                    json_filename = f"{prompt_filename}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
                except Exception as e:
                    print(str(e),  "Extraction did not work, save as string")
                    as_string = output.choices[0].message.content
                    json_filename = f"{prompt_filename}_{utils.random_id()}_{idx}.json"
                    utils.writeJSON(as_string,os.path.join(settings_run.directory_path,json_filename))
            except Exception as e: 
                print(idx)
                print(str(e))
                print("didnt work")

            
print("llama done.")




