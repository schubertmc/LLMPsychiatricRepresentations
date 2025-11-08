#fine_tuning.py

# Dataset Generation based on SimulatedPatientCharacteristics
from openai import OpenAI
import pandas as pd 
import json
import os

#### Functions ####
def writeJSON(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file)

def getPatientReport(
        prompt,
        model, 
        temperature,
        top_p,
        ):

    output = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        top_p=top_p,
        messages =  [ {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}],
    )
    return output



##############
client = OpenAI()
MODEL = "gpt-4o-mini"

#############
saving_dir = "../AgeAdjustedSCZDataset"
os.mkdir(saving_dir)
data = pd.read_csv("../Schizophrenia_SimulatedPatientCharacteristics.csv")

for idx, row in data.iterrows():
    print(idx, row)
    patient_id = row["patient_id"]
    sex = row["sex_name"].lower()
    age_of_onset = row["age_exact"]
    prompt = f"Please create a short patient report for a {sex} patient with schizophrenia with an age of onset of {age_of_onset} years."
    print(sex, age_of_onset)

    output = getPatientReport(prompt=prompt,
        model=MODEL,
        temperature=1,
        top_p=1)

    print(output.choices[0].message.content)
    data_to_save = {"patient_id": patient_id,
                    "sex_name": age_of_onset,
                    "prompt":prompt,
                    "generated_patient_report":output.choices[0].message.content
    }
    filename = f"PatientReport_{patient_id}.json"
    writeJSON(data_to_save, os.path.join(saving_dir, filename))
