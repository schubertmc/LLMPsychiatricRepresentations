#bpatientreports.py # batch version 


import os
import json
import utils
from data_processing import summarizePatientData

from dotenv import load_dotenv # type: ignore
load_dotenv(".env")

import anthropic # type: ignore
from openai import OpenAI # type: ignore
import openai
from openai.lib._parsing._completions import type_to_response_format_param # type: ignore
import requests

from concurrent.futures import ThreadPoolExecutor
import time

openai_client = OpenAI()

anthropic_client = anthropic.Anthropic() # print(anthropic.__version__) # 0.34.1 previously, now 0.42.0

togetherai_client = openai.OpenAI(
  api_key= os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)


EXXA_headers = {"X-API-Key": os.getenv("X-API-Key"),
            "Content-Type": "application/json"}

#import replicate # type: ignore
#import visualization
#import data_processing
#from openai.lib._pydantic import to_strict_json_schema # type: ignore




# Openai batch command creation
def createBatchLine_OpenAI(settings, n, custom_idx=None):
    custom_id = settings.unique_name  + "_" + str(custom_idx)
    batch_line = {"custom_id": custom_id, 
              "method": "POST", 
              "url": "/v1/chat/completions", 
              "body": {"model": settings.model, 
                        "temperature": settings.temperature,
                        "top_p": settings.top_p,
                        "n": n,
                       "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": settings.prompt            
        } 
    
        ], 
        "response_format": type_to_response_format_param(settings.response_format)
    }}
    return batch_line



# Anthropic batch command creation
def createBatchLine_Anthropic(settings, tool_choice_name, custom_id):
    response_format_list = settings.response_format
    batch_line = {
            "custom_id": custom_id,
            "params": {
                "model": settings.model,
                "max_tokens": 4096, #1024 for normal run
                "temperature": settings.temperature,
                "tools" : response_format_list,
                "tool_choice":{"type": "tool", "name": tool_choice_name},
                "system": "You are a helpful assistant.",
                "messages": [
                   {
                         "role": "user",
                            "content": settings.prompt,
                     }
                ],
            },
        }
    return batch_line



# llama batch command creation
def createBatchLine_EXXA(settings, n=1, custom_idx=None):
    custom_id = settings.unique_name  + "_" + str(custom_idx)
    request = {
        "metadata": {"custom_id": custom_id},
    "request_body": {
    "model": settings.model,
    "temperature": settings.temperature,
    "top_p": settings.top_p,
    "n":n,
    "messages": [
        {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content":  settings.prompt            
            }
    ],
    "response_format": type_to_response_format_param(settings.response_format)
    }
    }
    return request



# Further information batch command creation
def createFurtherInformationLine_OpenAI(details_settings,
                                 original_settings, 
                                 patient_report_all, 
                                 custom_id
                                 ):    
    batch_line = {"custom_id": custom_id, 
              "method": "POST", 
              "url": "/v1/chat/completions", 
              "body": {"model": details_settings.model, 
                        "temperature": details_settings.temperature,
                        "top_p": details_settings.top_p,
                        "n": 1,
                       "messages":  [ {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please create a patient report for a patient with {original_settings['diagnosis']}."}, 
                    {"role": "assistant", "content": patient_report_all},
                    {"role": "user", "content": "Please return further information."}
                    ], 
        "response_format": type_to_response_format_param(details_settings.response_format)
    }}
    return batch_line


# Further information batch command creation
def createFurtherInformationLine_Anthropic(details_settings, 
                                           original_settings,
                                 patient_report_all, 
                                 tool_choice_name, 
                                 custom_id):
    response_format_list = details_settings.response_format
    batch_line = {
            "custom_id": custom_id,
            "params": {
                "model": details_settings.model,
                "max_tokens": 1024,
                "temperature": details_settings.temperature,
                "tools" : response_format_list,
                "tool_choice":{"type": "tool", "name": tool_choice_name},
                "system": "You are a helpful assistant.",
                "messages": [
                    {"role": "user", "content": f"Please create a patient report for a patient with {original_settings['diagnosis']}."}, 
                    {"role": "assistant", "content": patient_report_all},
                    {"role": "user", "content": "Please return further information."}
                ],
            },
        }
    return batch_line





# Further information batch command creation
def createFurtherInformationLine_EXXA(details_settings,
                                original_settings,
                                 patient_report_all, 
                                 custom_id):

    request = {
        "metadata": {"custom_id": custom_id},
    "request_body": {
    "model": details_settings.model,
    "temperature": details_settings.temperature,
    "top_p": details_settings.top_p,
    "n":1,
    "messages":[ {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please create a patient report for a patient with {original_settings['diagnosis']}."}, 
                    {"role": "assistant", "content": patient_report_all},
                    {"role": "user", "content": "Please return further information."}
                    ],
    "response_format": type_to_response_format_param(details_settings.response_format)
    }
    }
    return request




# Create batch files for main cohort
def large_cohort_batchfiles(settings_run,
                        mode,
                      n_patients=1,
                      n_sets=1, 
                      n_patients_per_set=1, 
                      tool_choice_name = "patient_report"):

    batch_lines = []
    if mode == "openai":
        for set_idx in range(n_sets):
            batch_lines.append(createBatchLine_OpenAI(settings_run, n_patients_per_set, custom_idx=set_idx))
    elif mode == "anthropic":
        for pat_idx in range(n_patients):
            custom_id = f"{settings_run.unique_name}_{pat_idx}"
            batch_lines.append(createBatchLine_Anthropic(settings_run, tool_choice_name, custom_id))
    elif mode == "llama":
        for pat_idx in range(n_sets):
            custom_id = f"{settings_run.unique_name}_{pat_idx}"
            batch_lines.append(createBatchLine_EXXA(settings_run, n_patients_per_set, custom_idx=pat_idx))

    # write batch lines to jsonl file 
    utils.writeJSONL(batch_lines, os.path.join(settings_run.directory_path, f"BatchReqs_{settings_run.unique_name}.jsonl"))
    


# Create batch files for further information
def create_details_batchfiles(details_settings,original_settings, field, mode, tool_choice_name, information_file = "structured.json"):
    
    files = os.listdir(details_settings.directory_path)
    reports_file = [file for file in files if file.endswith(information_file)][0]
    with open(os.path.join(details_settings.directory_path,reports_file)) as f:
        reports = json.load(f)


    batch_lines = []
    for idx, report_id in enumerate(reports):
        print("Processing report: ", idx)
        batch_line = None
        report_data = reports[report_id]
        patient_report_all = summarizePatientData(report_data, slots = ["chars", "details"])
        custom_id = f"{field}_{report_id}"

        if mode == "openai":
            batch_line = createFurtherInformationLine_OpenAI(details_settings=details_settings, 
                                                             original_settings=original_settings,
                                                            patient_report_all=patient_report_all, 
                                                            custom_id = custom_id)
        elif mode == "anthropic":
            batch_line = createFurtherInformationLine_Anthropic(details_settings=details_settings,
                                                                original_settings=original_settings,
                                                                patient_report_all=patient_report_all,
                                                                tool_choice_name=tool_choice_name,
                                                                custom_id=custom_id)
        elif mode == "llama":
            batch_line = createFurtherInformationLine_EXXA(details_settings=details_settings, 
                                              original_settings=original_settings, 
                                              patient_report_all=patient_report_all, 
                                              custom_id = custom_id)
        batch_lines.append(batch_line)

    utils.writeJSONL(batch_lines, os.path.join(details_settings.directory_path, f"BatchReqs_{details_settings.unique_name}.jsonl"))





def send_request(request, idx, file):
    print(f"Sending request: {idx} - {file}")
    response = requests.post(
        "https://api.withexxa.com/v1/requests", headers=EXXA_headers, json=request
    )
    return response.json()["id"]

def parallel_request_sending(batch_lines, file, groupid, max_workers=10):
    """Function to parallelize request sending."""
    # Use ThreadPoolExecutor to send requests concurrently
    request_ids = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(send_request, request, idx, file)
            for idx, request in enumerate(batch_lines)
        ]
        for future in futures:
            try:
                request_ids.append(future.result())
            except Exception as e:
                print(f"Error: {e}")

    # Create the batch request
    request_createbatch = {
        "requests_ids": request_ids,
        "metadata": {"batch_name": groupid + file}
    }
    return request_createbatch


# Send files to APIs and start batch
def sendAndStartBatchFile(dir, file, groupid="", mode="openai", parallel_mode = False):
    
    if mode == "openai":
        file_path = os.path.join(dir, file)
        batch_input_file = openai_client.files.create(
            file=open(file_path, "rb"),
            purpose="batch"
        )
        batch_input_file_id = batch_input_file.id
        print(batch_input_file_id)
        bx = openai_client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": groupid + file
            }
        )
        status = openai_client.batches.retrieve(bx.id)
        print(bx.id)
        print(status)
        return bx.id
    
    elif mode == "anthropic":
        file_path = os.path.join(dir, file)
        with open(file_path, "r") as f:
            batch_lines = f.readlines()
        batch_lines = [json.loads(line) for line in batch_lines]
        message_batch = anthropic_client.beta.messages.batches.create(
            requests = batch_lines
        )
        return message_batch.id
    
    elif mode == "llama":
        file_path = os.path.join(dir, file)
        with open(file_path, "r") as f:
            batch_lines = f.readlines()
        batch_lines = [json.loads(line) for line in batch_lines]

        if parallel_mode == False:
            request_ids = []
            for idx, request in enumerate(batch_lines):
                print("Sending request: ", idx, "-", file)
                response = requests.post("https://api.withexxa.com/v1/requests", headers=EXXA_headers, json=request)
                request_ids.append(response.json()["id"])

            request_createbatch = {
                "requests_ids": request_ids,
                "metadata": {"batch_name": groupid + file}
            }
            url = "https://api.withexxa.com/v1/batches"
            response_batchcreation = requests.post(url, headers=EXXA_headers, json=request_createbatch)
            batch_creation = response_batchcreation.json()
            batch_id = batch_creation["id"]
            return batch_id
        else:
            print("Parallel mode: ", parallel_mode)
            request_createbatch = parallel_request_sending(batch_lines, file=file, groupid="", max_workers=50)


            url = "https://api.withexxa.com/v1/batches"
            response_batchcreation = requests.post(url, headers=EXXA_headers, json=request_createbatch)
            
            print(response_batchcreation) # <Response [404]>
            print("Error in batch creation: ", response_batchcreation.text)
            
            batch_creation = response_batchcreation.json()
            batch_id = batch_creation["id"]
            return batch_id





 





