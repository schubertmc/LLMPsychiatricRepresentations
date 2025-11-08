# generate patient datasets


import os
import batch_patientreports as cx 
from settings_classes import Settings
import response_formats
import utils

import apatientreports as apr
import openai
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
n_patients = 100


response_format_PYDANTIC =response_formats.Reports
response_format_TOOLS = response_formats.response_format_tools_Reports
target_structure_GEN = response_formats.Reports_target_structure
TEMP_WITH = "06_prompt_multiplereports_withResponseFormat.j2"
TEMP_WITHOUT = "06_prompt_multiplereports_withoutResponseFormat.j2"
##GENERAL PARAMS


# dictionary of all the disorders
disorder_dict = {
   "MDD": "major depressive disorder",
   "SCZ": "schizophrenia",
   "ADHD": "attention-deficit/hyperactivity disorder",
    "AUT": "autism spectrum disorder",
    "CD": "conduct disorder",
   "ED": "eating disorder",
    "ANX": "anxiety disorder",
    "BIP": "bipolar disorder",
}


# LLM 1
os.chdir(main_dir)
modelmode = "openai"

# create directory
directory_path = os.path.join("data/06_MultReps/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path) 

for disorder_short, disorder_long in disorder_dict.items():
    print(disorder_short, disorder_long)
    settings_run = Settings(
    unique_name=f"{modelmode}_{disorder_short}_V1",
    model = "gpt-4o-mini",
    diagnosis_long=disorder_long,
    diagnosis_short=disorder_short,
    temperature=1,
    top_p=1,
    prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"disorder_long": disorder_long}),
    response_format = response_format_PYDANTIC, 
    target_structure=target_structure_GEN
    )
    
    # create batch files here
    cx.large_cohort_batchfiles(settings_run, n_sets=1, n_patients_per_set=5, mode = modelmode)
    batch_id = cx.sendAndStartBatchFile(settings_run.directory_path, f"BatchReqs_{settings_run.unique_name}.jsonl", groupid="", mode=modelmode)
    settings_run.batch_id = batch_id
    settings_run.save_settings()




# LLM 2
os.chdir(main_dir)
modelmode = "anthropic"

# create directory
directory_path = os.path.join("data/06_MultReps/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path) 

for disorder_short, disorder_long in disorder_dict.items():
    print(disorder_short, disorder_long)
    settings_run = Settings(
    unique_name=f"{modelmode}_{disorder_short}_V1",
    model = "claude-3-haiku-20240307",
    diagnosis_long=disorder_long,
    diagnosis_short=disorder_short,
    temperature=1,
    top_p=1,
    prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITHOUT, params={"disorder_long": disorder_long}) + "Ensure that all fields are filled. Do not use placeholders such as <UNKNOWN> or null",
    response_format = response_format_TOOLS, 
    target_structure=target_structure_GEN
    )

    cx.large_cohort_batchfiles(settings_run, n_patients=5, mode = modelmode, tool_choice_name = "reports")
    
    batch_id = cx.sendAndStartBatchFile(settings_run.directory_path, f"BatchReqs_{settings_run.unique_name}.jsonl", groupid="", mode=modelmode)
    settings_run.batch_id = batch_id
    settings_run.save_settings()




# LLM 3
os.chdir(main_dir)
# use together ai api 
modelmode = "llama"



# create directory
directory_path = os.path.join("data/06_MultReps/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path) 


reports = []
for disorder_short, disorder_long in disorder_dict.items():
    print(disorder_short, disorder_long)
    settings_run = Settings(
    unique_name=f"{modelmode}_{disorder_short}_V1",
    model =  "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", #exxa;llama-3.1-8b-instruct-fp16" for together-ai: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    diagnosis_long=disorder_long,
    diagnosis_short=disorder_short,
    temperature=0.95,
    top_p=1,
    prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITH, params={"disorder_long": disorder_long}),
    response_format = response_format_PYDANTIC, 
    target_structure=target_structure_GEN
    )
    # create batch files

    for n_runs in range(10):
        print("Run number:", n_runs)
        # create batch files here
        output = apr.getPatientReport_Tog(
                    togetherai_client=togetherai_client,settings=settings_run, 
                    n=1)
        
        try: 
            as_dict = json.loads(output.choices[0].message.content)
            reports.append(as_dict)
            json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{utils.random_id()}_{n_runs}.json"
            utils.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))
        except Exception as e:
            print(str(e),  "Extraction did not work, save as string")
            as_string = output.choices[0].message.content
            reports.append(as_string)
            json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{utils.random_id()}_{n_runs}_unclean.json"
            utils.writeJSON(as_string,os.path.join(settings_run.directory_path,json_filename))
        settings_run.save_settings()

    settings_run.save_settings()

print("Done.")





