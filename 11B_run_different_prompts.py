


import os
import data_processing
import pandas as pd



base_path = "../MAIN/"


modelmodes = ["openai", "anthropic", "llama"]

base_folder= os.path.join(base_path,"data/02_Prompts")
os.chdir(base_folder)


dfs = []
for modelmode in modelmodes:
	directory_path = os.path.join(base_folder, modelmode)
	os.chdir(directory_path)
	prompts = os.listdir(directory_path)
	prompts =[p for p in prompts if not p.endswith(".DS_Store")]
	for prompt in 	prompts:
		path = os.path.join(directory_path, prompt)
		data = data_processing.bindReportsFromFolder(path, filename=True)
		data["modelmode"] = modelmode
		dfs.append(data)
	print(f"{modelmode} done.")



bound = pd.concat(dfs)
bound.to_csv(os.path.join(base_folder, "different_prompts.csv"))


print("Done")


####
