#21C_multieReports_BuildDataframes.py

import os
import pandas as pd
import data_processing

main_dir = "../MAIN/"
os.chdir(main_dir)


#
modelmodes = ["anthropic", "openai"]
#modelmodes = ["llama"]
slots_to_bind = ["chars", "details","PHQ9", "PANSS"]

#information_file = "structured.json"# basic 

# Main run: 
information_file = "structured.json"

for modelmode in modelmodes: 
    folder_path = os.path.join(main_dir, "data/06_MultReps/", modelmode)
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]

    patient_list = []
    dfs = []
    for folder in folders: 
        current_path = os.path.join(folder_path, folder)
        files = os.listdir(current_path)
        json_files =  [file for file in files if file.endswith(information_file)]
        for json_file in json_files:
            print(json_file)
            try: 
                patient_list = data_processing.extractInformationFromFile_vBatch_MultipleReports(current_path=current_path, json_file=json_file, 
                                                                          slots=slots_to_bind
                                                                          )
                len(patient_list)
                if patient_list == []:
                    print("No data extracted from folder", folder)
                else:
                    # create a pandas dataframe from the list of dictionaries
                    df = pd.DataFrame(patient_list)
                    df.to_csv(os.path.join(current_path, "detailed_quants.csv"))
                    dfs.append(df)

            except Exception as e: 
                print(print("Exception: ",str(e),"in file", json_file))

       


    bound = pd.concat(dfs)
    bound.to_csv(os.path.join(main_dir, "data/06_MultReps",modelmode, f"detailed_quants_bound_{information_file}.csv"))


## llama: 



modelmodes = ["llama"]
slots_to_bind = ["chars", "details","PHQ9", "PANSS"]

#information_file = "structured.json"# basic 

# Main run: 

for modelmode in modelmodes: 
    folder_path = os.path.join(main_dir, "data/06_MultReps/", modelmode)
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]

    patient_list = []
    dfs = []
    for folder in folders: 
        current_path = os.path.join(folder_path, folder)
        files = os.listdir(current_path)
        print(files)
        json_files =  [file for file in files if not file.endswith("basesettings.json")]
        for json_file in json_files:
            print(json_file)
            try: 
                #patient_list = data_processing.bindReportsFromFolder(current_path=current_path, json_file=json_file, 
                #                                                          slots=slots_to_bind
                #                                                          )
                patient_list = data_processing.extractInformationFromFile_MultipleReports(current_path=current_path, json_file=json_file)
                len(patient_list)
                if patient_list == []:
                    print("No data extracted from folder", folder)
                else:
                    # create a pandas dataframe from the list of dictionaries
                    df = pd.DataFrame(patient_list)
                    dfs.append(df)

            except Exception as e: 
                print(print("Exception: ",str(e),"in file", json_file))


    bound = pd.concat(dfs)
    bound.to_csv(os.path.join(main_dir, "data/06_MultReps",modelmode, f"detailed_quants_bound.csv"))


