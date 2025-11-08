

import os
import json

# Temp topp anaylsis
import pandas as pd


base_path = "../MAIN/"

folder_paths = [
    os.path.join(base_path, "data/01_Parameters/llama"),
       os.path.join(base_path,"data/01_Parameters/anthropic"),
       os.path.join(base_path,"data/01_Parameters/openai")
]


for folder_path in folder_paths:
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    

    data_list = []
    for idx, folder in enumerate(folders): 
        #print(idx)
        files = os.listdir(os.path.join(folder_path, folder))
        files = [file for file in files if file.endswith(".json") and  not file.endswith("settings.json")]

        for file in files: 
            with open(os.path.join(folder_path,folder,file)) as f:
                data = f.read()
            
            patient_case = data.encode("utf-8", errors="replace").decode("unicode_escape", errors="replace")
            #print(patient_case)
            unicode_chars = {}
            for char in patient_case:
                if ord(char) > 127:  # Non-ASCII characters
                    unicode_chars[str(ord(char))] = unicode_chars.get(char, 0) + 1
                    #print("found: ", repr(char))

            chars = pd.DataFrame.from_dict(unicode_chars, orient="index", columns=["count"])
            n_unicode_unique = chars.shape[0]
            n_total = sum(chars["count"])

            row = {"folder_id": folder,
                "file_id": file,
                "patient_case":patient_case.encode("utf-8", errors="replace"), 
                "n_unique":n_unicode_unique,
                "n_total":n_total, 
                }
            try:
                data = json.loads(data)
                extracted_data = {
                    "sex": data["chars"]["sex"], 
                        "age_current": data["chars"]["age_current"],
                        "age_of_onset":data["chars"]["age_of_onset"]
                        }
                
                row.update(extracted_data)
            except Exception as e:
                print(str(e))
                print("couldnt extract chars")
                extracted_data = {
                            "sex": -1, 
                        "age_current": -1,
                        "age_of_onset":-1
                        }
                row.update(extracted_data)
        
            
            data_list.append(row)
            

    bound = pd.DataFrame.from_dict(data_list, dtype="object")

    bound.to_csv(os.path.join(folder_path,"TEMP_TOPP_CHARACTERANALYSIS.csv"))



print("Done")
