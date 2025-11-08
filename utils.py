import os
import json
import string 
import random 
import jinja2
import tiktoken # type: ignore
import data_processing
from datetime import datetime
import requests

from dotenv import load_dotenv # type: ignore
load_dotenv(".env")


from openai import OpenAI # type: ignore
openai_client = OpenAI()




import anthropic # type: ignore
anthropic_client = anthropic.Anthropic() # print(anthropic.__version__) # 0.34.1 previously, now 0.42.0


EXXA_headers = {"X-API-Key": os.getenv("X-API-Key"),
            "Content-Type": "application/json"}



def writeJSON(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file)

def writeJSONL(data_list, filename):
    with open(filename, "w") as file:
        for data in data_list:
            json.dump(data, file)
            file.write("\n")

def random_id(length=4):
    characters = string.ascii_uppercase + string.digits
    random_id = ''.join(random.choices(characters, k=length))
    return random_id


# Prompt template creation
def createPromptWithTemplate(prompt_dir, TEMPLATEFILE, params):
    templateLoader = jinja2.FileSystemLoader(searchpath=prompt_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(TEMPLATEFILE)
    outputText = template.render(**params)
    return outputText


# Batch retrieval functions
def getTargetSettingFiles(path, settingfile_ending):
    # Identify setting files
    os.chdir(path)
    settings_files = []
    for root, dirs, files in os.walk("."):
        print(dirs)
        for file in files:
            if file.endswith(settingfile_ending):
                settings_file = os.path.join(root, file)
                settings_files.append(settings_file) 
    return settings_files


# Batch retrieval functions
def retrieveData(settings, modelmode):
    # retrieve batch
    if modelmode == "openai":
        batch = openai_client.batches.retrieve(settings.batch_id)
        if batch.status == "completed":
            file = batch.metadata["description"].replace("BatchReqs", "BatchResponses")       
            file_response = openai_client.files.content(batch.output_file_id)
            txt = file_response.text
            # write jsonl 
            file_path = os.path.join(settings.directory_path, f"raw_{file}")
            print(file_path)
            with open(file_path, "w") as f:
                f.write(txt)
        else:
            print("Batch not completed")
    elif modelmode == "anthropic":
        # retrieve batch
        batch = anthropic_client.messages.batches.retrieve(settings.batch_id)
        print(batch)

        if batch.processing_status == "ended":
            responses_raw = []
            for result in anthropic_client.messages.batches.results(settings.batch_id):
                responses_raw.append(result.to_dict())

            # write jsonl
            file_path = os.path.join(settings.directory_path, f"raw_BatchResponses_{settings.unique_name}.jsonl")
            print(file_path)
            writeJSONL(responses_raw, file_path)
        else:
            print("Batch not completed")

    elif modelmode == "llama":
        batch_id = settings.batch_id
        status = requests.get(f"https://api.withexxa.com/v1/batches/{batch_id}/status", headers=EXXA_headers)
        status_loaded = json.loads(status.text)

        if status_loaded["status"] == "completed":
            print(f"Batch {batch_id} is completed. Retrieving results...")
            results = requests.get(f"https://api.withexxa.com/v1/batches/{batch_id}/results", headers=EXXA_headers)
            results_string= results.text
            splitted = results_string.splitlines()
            results = [json.loads(line) for line in splitted if line != ""]
            responses_raw = []
            for res in results:
                responses_raw.append(res)

            # write jsonl
            file_path = os.path.join(settings.directory_path, f"raw_BatchResponses_{settings.unique_name}.jsonl")
            print(file_path)
            writeJSONL(responses_raw, file_path)
        else:
            print("Batch not completed")






# Structure batch output data
def structureBatchData_Base(loaded_settings, modelmode, outputfile_ending="_structured.json"):
    # Load the settings
    unique_name = loaded_settings.unique_name
    # Load the data
    file_path = os.path.join(loaded_settings.directory_path, f"raw_BatchResponses_{unique_name}.jsonl")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            raw_data = f.readlines()

        # process data
        if modelmode == "openai":
            patient_reports = data_processing.process_to_structured(raw_data)
        elif modelmode == "anthropic":
            patient_reports = data_processing.process_to_structured_Anthropic(raw_data)
        elif modelmode == "llama":
            patient_reports = data_processing.process_to_structured_EXXA(raw_data)
        # assign unique reportid
        all_dict = {}
        for idx, report in enumerate(patient_reports):
               rid = f"{unique_name}_{random_id()}_{idx}"
               print(rid)
               all_dict.update({rid: report})
        # write data
        output_file = os.path.join(loaded_settings.directory_path, f"{unique_name}{outputfile_ending}")
        writeJSON(all_dict, output_file)

   
def structuredBatchData_Details(loaded_settings, modelmode, outputfile_ending, originalfile_ending, field_name):
    unique_name = loaded_settings.unique_name
    # Load the data
    file_path = os.path.join(loaded_settings.directory_path, f"raw_BatchResponses_{unique_name}.jsonl")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            raw_data = f.readlines()

        # process data
        if modelmode == "openai":
            details = data_processing.process_to_structured_withID(raw_data)
        elif modelmode == "anthropic":
            details = data_processing.process_to_structured_withID_Anthropic(raw_data)
        elif modelmode == "llama":
            details = data_processing.process_to_structured_withID_EXXA(raw_data)

        # load in original data
        unique_name = unique_name.replace(f"_{field_name}", "")
        original_data_path = os.path.join(loaded_settings.directory_path, f"{unique_name}{originalfile_ending}")
        with open(original_data_path, "r") as f:
            original_data = json.load(f)
        for key, value in details.items():
            print(key)
            rid = key.replace(f"{field_name}_", "")            
            original_data[rid].update({loaded_settings.field_name: value})

        # write data
        output_file = os.path.join(loaded_settings.directory_path, f"{unique_name}{outputfile_ending}")
        writeJSON(original_data, output_file)
        





#Batch Status checking functions

# check openai batch status
def checkBatches_OpenAI(limit=10): 
    batches = openai_client.batches.list(limit=limit)
    for batch in batches:
        print(batch.id, batch.status, batch.metadata)





def getChoiceDictionary(output): 
    try:
        out_message = output["result_body"]["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error: ", e)
        out_message = None
    return out_message

def getTime(parsed):
    timestamps =["created_at", "expires_at", "in_progress_at", "ended_at"]
    for stamp in timestamps:
        try:
            num = parsed[stamp]
            if num != None:
                string = datetime.fromtimestamp(num)
                print(stamp, ":", string)
        except:
            print(stamp, ":", None)
            pass


# list all requests
def checkRequests_EXXA():
    print("Checking requests...")
    response = requests.get("https://api.withexxa.com/v1/requests/", headers=EXXA_headers)
    out_string = response.text
    splitted = out_string.splitlines()
    reqs = [json.loads(line)  for line in splitted if line != ""]
    for req in reqs:
        print('\n########\n', req)
        requestid = req["id"]
        # get status
        output = requests.get("https://api.withexxa.com/v1/requests/" + requestid, headers=EXXA_headers)
        print("1", output.text)
        parsed = output.json()
        print("Metadata:", parsed["metadata"])
        getTime(parsed)
        out_dict = getChoiceDictionary(parsed)
        print("3",out_dict)

# list all requests
def checkBatches_EXXA(target_batch_id_list = None):
    if target_batch_id_list == None:
        print("Checking batches...")
        response = requests.get("https://api.withexxa.com/v1/batches/", headers=EXXA_headers)
        out_string = response.text
        splitted = out_string.splitlines()
        reqs = [json.loads(line)  for line in splitted if line != ""]
        for req in reqs:
            print('\n########\n', req)
            requestid = req["id"]
            try: 
                batch_name = req["metadata"]["batch_name"]
                print(batch_name)
            except Exception as e:
                pass
            # get status
            status = requests.get("https://api.withexxa.com/v1/batches/" + requestid + "/status", headers=EXXA_headers)
            status_loaded = json.loads(status.text)
            getTime(status_loaded)
            print(status_loaded["status"])
    
    else: 
        # check target_ids
        for target_batch_id in target_batch_id_list:
            print(target_batch_id)
            status = requests.get("https://api.withexxa.com/v1/batches/" + target_batch_id + "/status", headers=EXXA_headers)
            status_loaded = json.loads(status.text)
            getTime(status_loaded)
            print(status_loaded["status"])



# Token counting 
def countTokens(text:str, encoding):
    encoding = tiktoken.encoding_for_model('gpt-4')
    encoding.encode(text)
    return len(encoding.encode(text))



# calcualte costs
def calculateCosts(n_input_tokens, n_output_tokens, n_runs=1, 
                   model="gpt-4o-mini"
                   
                   ):
    
    #input tokens: 141
    #output tokens: 157


    if model == "gpt-4o-mini":
        input_price_ppM = 0.150
        output_price_ppM = 0.600
    elif model == "gpt-4o":
        input_price_ppM = 5
        output_price_ppM = 15
    elif model == "text-embedding-3-small":
        input_price_ppM = 0.020
        output_price_ppM = 0
    elif model == "text-embedding-3-large":
        input_price_ppM = 0.130
        output_price_ppM = 0
    elif model == "meta-llama-3-8b":
        input_price_ppM = 0.05
        output_price_ppM = 0.25
    

    input_cost = n_runs* (n_input_tokens * input_price_ppM / 1e6)
    output_cost = n_runs* (n_output_tokens * output_price_ppM / 1e6)
    total_cost = input_cost + output_cost
    print(f"total cost: {round(total_cost, 2)}$ with {model}")
    return total_cost







# deprecated
def clean_string(string_input, bracket = "curly"):
    open_bracket = "{"
    close_bracket = "}"
    if bracket == "square":
        open_bracket = "["
        close_bracket = "]"
    first_bracket_index = string_input.find(open_bracket)
    last_bracket_index = string_input.rfind(close_bracket)
    # replace every occurence of ' with "
    string_input = string_input.replace("'", '"')
    return string_input[first_bracket_index:last_bracket_index+1]



# deprecated
def validateJSONStructure(target_structure, json_obj):
    for target_key, target_value in target_structure.items():
        # Check if the key is in the json object
        if target_key not in json_obj:
            print(f"'{target_key}', not in json_obj")
            return False
        
        # If the key exists, check what kind of value is expected

        # dictionary
        if isinstance(target_value, dict):
            #print("Checking dict")
            if not isinstance(json_obj[target_key], dict):
                print(f"Invalid JSON: '{target_key}' is not a dict")
                return False
        
        # list
        elif isinstance(target_value, list):
            #print("Checking list")
            if not isinstance(json_obj[target_key], list):
                print(f"Invalid JSON: '{target_key}' is not a list")
                return False
        # other
        else:
            #print("Checking other type")
            if not isinstance(json_obj[target_key], target_value):
                return False
        #print(f"'{target_key}' passed check.")
    #print("Json valid.")
    return True


