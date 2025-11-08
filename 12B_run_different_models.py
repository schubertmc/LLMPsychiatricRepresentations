#run_different_models.py


import os
import data_processing


base_path = "../MAIN/"

modelmodes = ["openai", "anthropic", "llama"]

base_folder= os.path.join(base_path,"data/03_DifferentModels")
os.chdir(base_folder)


dfs = []
for modelmode in modelmodes:
	directory_path = os.path.join(base_folder, modelmode)
	os.chdir(directory_path)
	models = os.listdir(directory_path)
	models =[model for model in models if model.endswith("_structured")]
	for model in models:
		path = os.path.join(directory_path, model)
		data = data_processing.bindReportsFromFolder(path)
		data["model"] = model
		dfs.append(data)
	print(f"{modelmode} done.")
import pandas as pd

bound = pd.concat(dfs)
bound.to_csv(os.path.join(base_folder, "different_models.csv"))


print("Done")

