import os
from dotenv import load_dotenv # type: ignore
load_dotenv(".env")

import replicate # type: ignore
import anthropic # type: ignore

from openai import OpenAI # type: ignore
import openai
from data_processing import summarizePatientData
from datetime import datetime
import json
import utils
#import z_oldvisualization
import data_processing

from openai.lib._pydantic import to_strict_json_schema # type: ignore
from openai.lib._parsing._completions import type_to_response_format_param # type: ignore

anthropic_client = anthropic.Anthropic()
client = OpenAI()

togetherai_client = openai.OpenAI(
  api_key= os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)



# Patient Reports
def getPatientReport_nX(
        client,
        settings,
        n           # number of patient reports to create
        ):
    output = client.beta.chat.completions.parse(
        model=settings.model,
        temperature=settings.temperature,
        top_p=settings.top_p,
        n = n,
        messages =  [ {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": settings.prompt}],
                response_format=settings.response_format,
    )
    return output

def getPatientReport_Anthropic(
        settings,
        tool_choice_name
        ):
    response_format_list = settings.response_format
    output = anthropic.Anthropic().messages.create(
    model=settings.model,
    max_tokens=1024,
    temperature=settings.temperature,
#    top_p=settings.top_p,
    tools=response_format_list,
    tool_choice={"type": "tool", "name": tool_choice_name},
    system="You are a helpful assistant.",
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


def getPatientReport_Tog(
        # "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        togetherai_client,
        settings,
        n = 8,
        ):
#    print("Prompt:")
#    print(settings.prompt)
#    print(settings.response_format.model_json_schema())
#    print("----")

    output = togetherai_client.chat.completions.create(
    model=settings.model,
    temperature=settings.temperature,
    top_p=settings.top_p,
    n = n,
    messages=[
        {"role": "system","content": "You are a helpful assistant."},
        {"role": "user","content": settings.prompt},
    ],
    response_format={"type": "json_object",
      "schema": settings.response_format.model_json_schema()}
    )
    return output



def processOutput(settings_run, output, mode):
        #print("Processing output...")

        # llama mode is deprecated
        if mode == "llama":
            attempt_count = 0
            extracted_output = None
            while attempt_count < 4:
                try:

                    # Extraction
                    extracted_output = json.loads(utils.clean_string(output))

                    # Validation
                    if utils.validateJSONStructure(settings_run.target_structure, extracted_output):
                        print("Valid JSON and valid Structure.")
                        return extracted_output
                    
                    # If extracted but not valid, try to correct
                    print("Invalid JSON Structure, now getting valid JSON...")
                    output = getValidJSON_Rep(settings_run, output, settings_run.target_structure)

                except Exception as e: 
                    # If extraction fails, try to correct
                    print("Error extracting JSON: ", str(e),"with output:", output, "\n------Now trying to correct JSON...")           
                    output = getValidJSON_Rep(settings_run, output, settings_run.target_structure)


                attempt_count += 1
            

        elif mode == "anthropic":
            try:
                extracted_output = output.content[0].input

            except Exception as e:
                print("Error extracting JSON: ", str(e),"\n")
                print(output)


            return extracted_output
        else: 
            pass


def save_output(output, settings_run, idx):
    """Save the output to a JSON file."""
    try:
        json_filename = f"{settings_run.unique_name}_{utils.random_id()}_{idx}.json"
        utils.writeJSON(output, os.path.join(settings_run.directory_path, json_filename))
    except Exception as e:
        print(f"Error saving output for index {idx}: {e}")


def add_output_to_file(output, file_path):
    try:
        utils.writeJSON(output, file_path)
    except Exception as e:
        print(f"Error saving output to file {file_path}: {e}")




def run_large_cohort(settings_run,
                     mode="llama",
                      n_patients=1,
                      n_sets=1, 
                      n_patients_per_set=1, 
                      tool_choice_name = "patient_report"):

    generation_functions = {
        "llama": lambda settings, **kwargs: getPatientReport_Tog(togetherai_client=togetherai_client, settings=settings, n=kwargs["n"]),
        "openai": lambda settings, **kwargs: getPatientReport_nX(client=kwargs["client"], settings=settings, n=kwargs["n"]),
        "anthropic": lambda settings, **kwargs: getPatientReport_Anthropic(settings=settings, tool_choice_name=kwargs["tool_choice_name"])
    }
    # binding_functions = {
    #     "llama": lambda reports: data_processing.bindReports_dict(reports),
    #     "openai": lambda reports: data_processing.bindReports_dict(reports),
    #     "anthropic": lambda reports: data_processing.bindReports_dict(reports)
    # }


    def bind_and_visualize_reports(reports, binding_function):
        try:
            bound = binding_function(reports)
            print("###########\nResults:")
            print(bound["age_of_onset"].value_counts())
            print(bound["sex"].value_counts())
            print(bound["age_current"].value_counts())
            z_oldvisualization.plotting(bound, saving_dir=settings_run.directory_path)
            bound.to_csv(os.path.join(settings_run.directory_path, "quants.csv"))
        except Exception as e:
            print("Binding/Visualization error: ", str(e))


    reports = []
    
    if mode == "anthropic":
        for idx in range(n_patients):
            print(idx, "of", n_patients)
            output = ""
            extracted_output = ""
            start = datetime.now()
            output = generation_functions[mode](settings_run, tool_choice_name=tool_choice_name)
            end = datetime.now()
            print("Duration:", end-start)

            # process output 
            extracted_output = processOutput(settings_run, output, mode)
           
            reports.append(extracted_output)
            save_output(extracted_output, settings_run, idx)
    

    elif mode == "openai":
        print(settings_run)
        for i in range(n_sets):
            print(i, "of", n_sets, "sets")
            start = datetime.now()
            output = generation_functions[mode](settings_run, client=client, n=n_patients_per_set)
            end = datetime.now()
            print("Duration:", end-start)
            for idx, choice in enumerate(output.choices):
                #print(idx)
                as_dict = choice.message.parsed.dict()
                reports.append(as_dict)
                save_output(as_dict, settings_run, idx)  


    elif mode == "llama":
        for i in range(n_sets):
            print(i, "of", n_sets, "sets")
            start = datetime.now()
            output = generation_functions[mode](settings_run, n=n_patients_per_set)
            end = datetime.now()
            print("Duration:", end-start)
            for idx, choice in enumerate(output.choices):
                #print(idx)
                as_dict = json.loads(choice.message.content)
                reports.append(as_dict)
                save_output(as_dict, settings_run, idx)    

    else: 
        print("mode not implemented: ", mode)
    

    # bind and visualize reports
    bind_and_visualize_reports(reports, data_processing.bindReports_dict)
            



# Further Information Details

def getFurtherInformation_OpenAI(client, 
                                 details_settings, 
                                 original_settings,
                                 patient_report_all):
    output = client.beta.chat.completions.parse(
            model=details_settings.model,
            temperature=details_settings.temperature,
            top_p=details_settings.top_p,
            n = 1,
            messages =  [ {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please create a patient report for a patient with {original_settings['diagnosis']}."}, 
                    {"role": "assistant", "content": patient_report_all},
                    {"role": "user", "content": "Please return further information."}
                    ],
                    response_format=details_settings.response_format
        )
    return output


def getFurtherInformation_Anthropic(
        original_settings,details_settings, patient_report_all, tool_choice_name
        ):
    response_format_list = details_settings.response_format

    output = anthropic.Anthropic().messages.create(
    model=details_settings.model,
    max_tokens=1024,
    temperature=details_settings.temperature,
    tools=response_format_list,
    tool_choice={"type": "tool", "name": tool_choice_name},
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Please create a patient report for a patient with {original_settings['diagnosis']}."
                }
            ]
        }, 
                {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": patient_report_all
                }
            ]
        }, 
                {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please return further information."
                }
            ]
        }
        
    ],
    )
    return output 


def getFurtherInformation_Tog(
        # "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        togetherai_client,
        details_settings,
        original_settings,
        patient_report_all
        ):
    output = togetherai_client.chat.completions.create(
    model=details_settings.model,
    temperature=details_settings.temperature,
    top_p=details_settings.top_p,
    n = 1,
    messages =  [ {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please create a patient report for a patient with {original_settings['diagnosis']}."}, 
                    {"role": "assistant", "content": patient_report_all},
                    {"role": "user", "content": details_settings.prompt}
                    ],
    response_format={"type": "json_object",
      "schema": details_settings.response_format.model_json_schema()}
    )
    return output



def run_details(details_settings,original_settings, folder_path, field, mode, tool_choice_name):
    files = os.listdir(folder_path)
    files = [file for file in files if file.endswith("json")]
    files = [file for file in files if file.count("settings")==0]
    files = [file for file in files if file.count("unclean")==0]

    gen_details_functions = {
        "llama": lambda details_settings, original_settings, patient_report_all: getFurtherInformation_Tog(togetherai_client = togetherai_client, details_settings=details_settings, 
                                                         original_settings=original_settings,
                                                         patient_report_all =patient_report_all ),
        "openai": lambda details_settings, original_settings, patient_report_all: getFurtherInformation_OpenAI(client = client, 
                                                         details_settings =details_settings, 
                                                         original_settings=original_settings,
                                                         patient_report_all =patient_report_all),
        "anthropic": lambda details_settings, original_settings, patient_report_all: getFurtherInformation_Anthropic(details_settings=details_settings, 
                                                                original_settings=original_settings,
                                                                patient_report_all =patient_report_all,
                                                                tool_choice_name=tool_choice_name)
    } 

    for idx, file in enumerate(files): 
        if file.endswith("json"):
            print(idx, ". Current Patient report: ", file)

            try: 
                patient_data=None
                with open(os.path.join(folder_path,file)) as f:
                    patient_data = json.load(f)
                patient_report_all = summarizePatientData(patient_data, slots = ["chars", "details", "ethnicity"])



                output = gen_details_functions[mode](details_settings, original_settings, patient_report_all)

                if mode =="llama":
                    extracted_output = json.loads(output.choices[0].message.content)                
                elif mode =="anthropic":
                    extracted_output = processOutput(details_settings, output, mode)
                elif mode =="openai":
                    extracted_output = output.choices[0].message.parsed.dict()
                
                json_filename = file
                patient_data[field] = extracted_output
                add_output_to_file(patient_data, os.path.join(folder_path, json_filename))
            except Exception as e: 
                print("Error processing file: ", file, "Error: ", str(e))
                # write error to file 
                error_dict = {"error": str(e)}
                add_output_to_file(error_dict, os.path.join(folder_path, f"{file}error.json"))



