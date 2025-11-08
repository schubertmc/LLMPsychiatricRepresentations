# generate patient datasets

import os
import batch_patientreports as cx 
from settings_classes import Settings
import response_formats
import utils


#MAIN Directory
main_dir = "../MAIN/"
prompt_dir = os.path.join(main_dir, "code/prompts")
os.chdir(main_dir)


##GENERAL PARAMS
# anthropic settings:
n_patients = 10000

#openai settings
n_patients_per_set_openai = 100 # max100
n_sets_openai = 100

#llama settings
n_patients_per_set_llama = 100 # max 8
n_sets_llama = 100

response_format_PYDANTIC =response_formats.PatientReport
response_format_TOOLS = response_formats.response_format_tools_vPatientReport
target_structure_GEN = response_formats.PatientReport_target_structure
TEMP_WITH = "01_prompt_reports_withResponseFormat.j2"
TEMP_WITHOUT = "01_prompt_reports_withoutResponseFormat.j2"
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
directory_path = os.path.join("data/PatientDatasets/", modelmode)
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
    cx.large_cohort_batchfiles(settings_run, n_sets=n_sets_openai, n_patients_per_set=n_patients_per_set_openai, mode = modelmode)
    batch_id = cx.sendAndStartBatchFile(settings_run.directory_path, f"BatchReqs_{settings_run.unique_name}.jsonl", groupid="", mode=modelmode)
    settings_run.batch_id = batch_id
    settings_run.save_settings()




# LLM 2
os.chdir(main_dir)
modelmode = "anthropic"

# create directory
directory_path = os.path.join("data/PatientDatasets/", modelmode)
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

    cx.large_cohort_batchfiles(settings_run, n_patients=n_patients, mode = modelmode)
    
    batch_id = cx.sendAndStartBatchFile(settings_run.directory_path, f"BatchReqs_{settings_run.unique_name}.jsonl", groupid="", mode=modelmode)
    settings_run.batch_id = batch_id
    settings_run.save_settings()




# LLM 3
os.chdir(main_dir)
modelmode = "llama"

# create directory
directory_path = os.path.join("data/PatientDatasets/", modelmode)
os.makedirs(directory_path, exist_ok=True)
os.chdir(directory_path) 

for disorder_short, disorder_long in disorder_dict.items():
    print(disorder_short, disorder_long)
    settings_run = Settings(
    unique_name=f"{modelmode}_{disorder_short}_V1",
    model =  "llama-3.1-8b-instruct-fp16", #exxa; for together-ai: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    diagnosis_long=disorder_long,
    diagnosis_short=disorder_short,
    temperature=1,
    top_p=1,
    prompt= utils.createPromptWithTemplate(prompt_dir= prompt_dir, TEMPLATEFILE=TEMP_WITH, params={"disorder_long": disorder_long}),
    response_format = response_format_PYDANTIC, 
    target_structure=target_structure_GEN
    )
    # create batch files

    cx.large_cohort_batchfiles(settings_run, n_sets=n_sets_llama, n_patients_per_set=n_patients_per_set_llama, mode = modelmode)

    batch_id = cx.sendAndStartBatchFile(settings_run.directory_path, f"BatchReqs_{settings_run.unique_name}.jsonl", groupid="", mode=modelmode, parallel_mode=True)
    settings_run.batch_id = batch_id
    settings_run.save_settings()

print("Done.")



