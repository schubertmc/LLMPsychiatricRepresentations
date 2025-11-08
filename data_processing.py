import os
import json
import pandas as pd




def process_to_structured(raw_batchdata):
    patient_reports = []
    # process data
    for batch in raw_batchdata:
        batch = json.loads(batch)
        content = batch["response"]["body"]["choices"]
        for choice in content:
            choice = choice["message"]["content"]
            parsed = json.loads(choice)
            patient_reports.append(parsed)
    return patient_reports

def process_to_structured_withID(raw_batchdata):
    patient_reports = {}
    for batch in raw_batchdata:
        batch = json.loads(batch)
        content = batch["response"]["body"]["choices"][0]["message"]["content"]
        custom_id = batch["custom_id"]
        parsed = json.loads(content)
        patient_reports.update({custom_id: parsed})
    return patient_reports


def process_to_structured_Anthropic(raw_batchdata):
    patient_reports = []
    for batch in raw_batchdata:
        batch = json.loads(batch)
        content = batch["result"]["message"]["content"][0]["input"]
        patient_reports.append(content)
    return patient_reports



def process_to_structured_withID_Anthropic(raw_batchdata):
    patient_reports = {}
    for batch in raw_batchdata:
        batch = json.loads(batch)
        content = batch["result"]["message"]["content"][0]["input"]
        custom_id = batch["custom_id"]
        patient_reports.update({custom_id: content})
    return patient_reports



def process_to_structured_EXXA(raw_batchdata):
    patient_reports = []
    # process data
    for batch in raw_batchdata:
        batch = json.loads(batch)
        content = batch["result_body"]["choices"]
        for choice in content:
            choice = choice["message"]["content"]
            parsed = json.loads(choice)
            patient_reports.append(parsed)
    return patient_reports


def process_to_structured_withID_EXXA(raw_batchdata):
    patient_reports = {}
    for batch in raw_batchdata:
        batch = json.loads(batch)
        content = batch["result_body"]["choices"][0]["message"]["content"]
        custom_id = batch["metadata"]["custom_id"]
        parsed = json.loads(content)
        patient_reports.update({custom_id: parsed})
    return patient_reports







def bindReports(list_of_reports):
    data_list = []
    for report in list_of_reports:
        cur_row = {"sex": report.chars.sex, 
                   "age_current": report.chars.age_current,
                   "age_of_onset":report.chars.age_of_onset
                   }
        data_list.append(cur_row)
    df = pd.DataFrame(data_list)
    return df

def bindReportsFromFolder(folder_path, filename = False):
    files = os.listdir(folder_path)
    #settings_path = [file for file in files if file.endswith("settings.json")][0]
    #with open(os.path.join(folder_path,settings_path)) as f:
    #    settings = json.load(f)
    json_files =  [file for file in files if file.endswith(".json") and not file.endswith("settings.json")]
    data_list = []
    for fx in json_files:
        with open(os.path.join(folder_path,fx)) as f:
            data = json.load(f)
        try:
            cur_row = {"sex": data["chars"]["sex"], 
                    "age_current": data["chars"]["age_current"],
                    "age_of_onset":data["chars"]["age_of_onset"]
                    }
            if filename:
                cur_row["filename"] = fx
            data_list.append(cur_row)
        except Exception as e:
            print(str(e))
            print("couldnt extract chars")
            cur_row = {"sex": -1, 
                       "age_current": -1,
                    "age_of_onset":-1
                    }
    df = pd.DataFrame(data_list)
    return df
        



def summarizePatientData(patient_data, slots = ["chars", "details"]):
    try:
        patient_report = patient_data["patient_report"]
        patient_dict = {}
        patient_dict["patient_report"] = patient_report
        print("Slots requested: ", slots)
        slots = [slot for slot in slots if slot in patient_data.keys()]
        print("Using slots: ", slots)
        for slot in slots:
            for key in patient_data[slot].keys():
                patient_dict[key] = patient_data[slot][key]

        patient_report_all=""
        for key in patient_dict.keys():
            patient_report_all += f"{key}: {patient_dict[key]}\n" 
    except Exception as e:
        print("Error in summarizePatientData: ", str(e),"; Patient data:", patient_data, "; slots: ", slots)
        patient_report_all = json.dumps(patient_data)
    return patient_report_all








def bindReports_dict(list_of_reports):
    data_list = []
    for report in list_of_reports:
        try:
            cur_row = {"sex":     report["chars"]["sex"], 
                        "age_current": report["chars"]["age_current"],
                        "age_of_onset":report["chars"]["age_of_onset"]
                        }
            data_list.append(cur_row)
        except Exception as e: 
            print(str(e))
            print(report)
    df = pd.DataFrame(data_list)
    return df


def bindReports_Details(list_of_reports):
    data_list = []
    for report in list_of_reports:
        cur_row = {"ethnicity": report.ethnicity, 
                   "BMI": report.BMI,
                   "smoking":report.smoking,
                   "education":report.education,
                   "socioeconomic_status":report.socioeconomic_status,
                   }
        data_list.append(cur_row)
    df = pd.DataFrame(data_list)
    return df


def bindReports_Details_FromFiles(folder_path):
    data_list = []
    files = os.listdir(folder_path)
    files = [file for file in files if file.endswith("json")]
    files = [file for file in files if file.count("settings")==0]
    files = [file for file in files if file.count("unclean")==0]
    for json_file in files:
        with open(os.path.join(folder_path,json_file)) as f:
            data = json.load(f)

        try:
            cur_row = {"ethnicity": data["ethnicity"], 
                    "BMI": data["BMI"],
                    "smoking": data["smoking"],
                    "education": data["education"],
                    "socioeconomic_status": data["socioeconomic_status"]
                    }
            data_list.append(cur_row)
        except Exception as e:
            print(str(e))
            print("Error in file: ", json_file)
            print(data)
    df = pd.DataFrame(data_list)
    return df


def extractInformationFromFile(current_path, json_file, slots = ["chars", "details"]):
    with open(os.path.join(current_path,json_file)) as f:
        data = json.load(f)

    patient_dict = {}
    patient_report = data["patient_report"]
    print("Slots requested: ", slots)
    slots = [slot for slot in slots if slot in data.keys()]
    print("Using slots: ", slots)

    patient_dict.update({
        "json_file": json_file,
        "patient_report": patient_report})
    for slot in slots:
        for key in data[slot].keys():
            patient_dict[key] = data[slot][key]

    return patient_dict



def extractInformationFromFile_MultipleReports(current_path, json_file, slots = ["chars", "details"]):
    with open(os.path.join(current_path,json_file)) as f:
        data = json.load(f)
    
    patient_list = []
    for idx, report in enumerate(data["reports"]):
        patient_dict = {}

    
        print("Slots requested: ", slots)
        slots = [slot for slot in slots if slot in report.keys()]
        print("Using slots: ", slots)

        patient_dict.update({
            "json_file": json_file + f"_{idx}",
            "patient_report": report["patient_report"]})
        for slot in slots:
            for key in report[slot].keys():
                patient_dict[key] = report[slot][key]
        patient_list.append(patient_dict)
    return patient_list
    




def extractInformationFromFile_vBatch(current_path, json_file, slots = ["chars", "details"]):
    with open(os.path.join(current_path,json_file)) as f:
        alldata = json.load(f)

    patient_list = []
    for rid, data in alldata.items():
        patient_dict = {}
        patient_dict["rid"] = rid
        patient_dict["json_file"] = json_file
        patient_dict["patient_report"] = data["patient_report"]
        print("Slots requested: ", slots)
        slots = [slot for slot in slots if slot in data.keys()]
        print("Using slots: ", slots)
        for slot in slots:
            for key in data[slot].keys():
                patient_dict[key] = data[slot][key]
    
        patient_list.append(patient_dict)
    return patient_list




def extractInformationFromFile_vBatch_MultipleReports(current_path, json_file, slots = ["chars", "details"]):
    with open(os.path.join(current_path,json_file)) as f:
        alldata = json.load(f)

    patient_list = []
    for rid, data in alldata.items():
        for report in data["reports"]:
            patient_dict = {}
            patient_dict["rid"] = rid
            patient_dict["json_file"] = json_file
            #patient_dict["reports"] = data["reports"]
            patient_dict["patient_report"] = report["patient_report"]
            
            print("Slots requested: ", slots)
            slots = [slot for slot in slots if slot in report.keys()]
            print("Using slots: ", slots)
            for slot in slots:
                for key in report[slot].keys():
                    patient_dict[key] = report[slot][key]

            patient_list.append(patient_dict)
    return patient_list





# def summarizePatientData(patient_data):
#     try:
#         patient_report = patient_data["patient_report"]
#         patient_sex = patient_data["chars"]["sex"]
#         patient_age_current = patient_data["chars"]["age_current"]
#         patient_age_of_onset = patient_data["chars"]["age_of_onset"] 
#         patient_report_all = f"""Sex: {patient_sex}\nCurrent Age: {patient_age_current}\nAge of Onset: {patient_age_of_onset}\n{patient_report}"""
#     except Exception as e:
#         patient_report_all = json.dumps(patient_data)
#     return patient_report_all
