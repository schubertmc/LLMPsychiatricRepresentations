


import os
import sys
from textwrap import dedent
from openai import OpenAI
from datetime import datetime  

import apatientreports as cx
from utils import random_id



os.chdir("/Users/marcschubert/Documents/MED/RCT_Sim_Psych/MAIN/data/Finetuning")


client = OpenAI()




### Run Age Adjusted Models


######### Run 
path = "/Users/marcschubert/Documents/MED/RCT_Sim_Psych/MAIN/data/Finetuning"
os.chdir(path)

#  Schizophrenia Age Adjusted
settings_run = cx.Settings(
unique_name="finetuning_ageadjusted-SCZ",
model ="ft:....",
temperature=1,
top_p=1,
prompt="""
Please create a short patient report for a patient with schizophrenia.
""",
response_format = cx.PatientReport
)
print(settings_run)

vignettes = []

for i in range(10):
    print(i)
    start = datetime.now()
    output =  output = cx.getPatientVignette_nX(
                    client=client,settings=settings_run, 
                    n=100)
    end = datetime.now()
    print(end-start)
    len(output.choices)
    for idx, choice in enumerate(output.choices):
        #print(idx)
        as_dict = choice.message.parsed.dict()
        vignettes.append(choice.message.parsed)
        json_filename = f"{settings_run.unique_name}_temp{settings_run.temperature}_topp{settings_run.top_p}_{random_id()}_{idx}.json"
        cx.writeJSON(as_dict,os.path.join(settings_run.directory_path,json_filename))


bound = cx.bindVignettes(vignettes) # - # - # - # - #

print(bound["age_of_onset"].value_counts())
print(bound["age_current"].value_counts())
print(bound["sex"].value_counts())
cx.plotting(bound, saving_dir=settings_run.directory_path)
bound.to_csv(os.path.join(settings_run.directory_path, "quants.csv"))



