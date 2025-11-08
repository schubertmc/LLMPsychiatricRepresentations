import uuid
import os
import json
from utils import writeJSON


####### Settings ##########

class Settings: 
    def __init__(self,
                 unique_name, 
                 model,
                 temperature,
                 top_p, 
                 prompt,
                 diagnosis_long,
                 diagnosis_short, 
                 response_format, 
                 target_structure,
                 create_data_folder=True):
        self.unique_id =uuid.uuid4().hex
        self.create_data_folder = create_data_folder
        self.unique_name = unique_name
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.prompt = prompt
        self.diagnosis = diagnosis_long
        self.diagnosis_short = diagnosis_short
        self.response_format = response_format
        self.target_structure = target_structure
        self.directory_path = self.create_directory()
        self.batch_id = ""
        self.field_name = ""
        self.save_settings()

    def create_directory(self):
        if self.create_data_folder == True:
            directory_name = f"{self.unique_name}_{self.unique_id}"
            try:
                os.makedirs(directory_name, exist_ok=True)
                print(f"Settings initialized. Folder created:\n{os.path.abspath(directory_name)}")
                return os.path.abspath(directory_name)
            except Exception as e:
                print(str(e))
                return None        
        else:
            directory_name = f"{self.unique_name}_{self.unique_id}"
        

    def to_dict(self):
        return {
            "unique_name": self.unique_name,
            "unique_id": self.unique_id,
            "model": self.model,
            "diagnosis": self.diagnosis,
            "diagnosis_short": self.diagnosis_short,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "prompt": self.prompt,
            "response_format": str(self.response_format),
            "target_structure": str(self.target_structure),
            "directory_path": self.directory_path, 
            "batch_id": self.batch_id, 
            "field_name": self.field_name
        }
    
    def save_settings(self):
        settings_filename = os.path.join(self.directory_path, f"{self.unique_name}_basesettings.json")
        writeJSON(self.to_dict(), settings_filename)


    @classmethod
    def from_dict(cls, data):
        instance = cls.__new__(cls)
        
        # Manually set attributes based on the dictionary
        instance.unique_id = data["unique_id"]
        instance.unique_name = data["unique_name"]
        instance.model = data["model"]
        instance.temperature = data["temperature"]
        instance.top_p = data["top_p"]
        instance.prompt = data["prompt"]
        instance.diagnosis = data["diagnosis"]
        instance.diagnosis_short = data["diagnosis_short"]
        instance.response_format = data["response_format"]
        instance.target_structure = data["target_structure"]
        instance.create_data_folder = False
        instance.directory_path = data["directory_path"]
        instance.batch_id = data["batch_id"]

        return instance

    @classmethod
    def load_settings(cls, filepath):
        # Load settings from a JSON file
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return None

        
    def __repr__(self):
        return (f"Settings:{self.unique_id},\n {self.unique_name}, {self.model}, "
                f"\nTemperature={self.temperature}, \nTop_p={self.top_p}, "
                f"\nPrompt='{self.prompt}', \nResponse Format='{self.response_format}')")



class DetailsSettings:
    def __init__(self,unique_name, model,temperature,top_p, prompt,response_format,target_structure, directory_path, field_name):
            self.unique_id =uuid.uuid4().hex
            self.unique_name = unique_name
            self.model = model
            self.temperature = temperature
            self.top_p = top_p
            self.prompt = prompt
            self.response_format = response_format
            self.target_structure = target_structure
            self.directory_path = directory_path# the current folder 
            self.batch_id = ""
            self.field_name = field_name
            self.save_settings()

    def to_dict(self):
        return {
            "unique_name": self.unique_name,
            "unique_id": self.unique_id,
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "prompt": self.prompt,
            "response_format": str(self.response_format), 
            "target_structure": str(self.target_structure), 
            "directory_path": self.directory_path,
            "batch_id": self.batch_id, 
            "field_name": self.field_name
        }
    

    @classmethod
    def from_dict(cls, data):
        instance = cls.__new__(cls)
        
        # Manually set attributes based on the dictionary
        instance.unique_id = data["unique_id"]
        instance.unique_name = data["unique_name"]
        instance.model = data["model"]
        instance.temperature = data["temperature"]
        instance.top_p = data["top_p"]
        instance.prompt = data["prompt"]
        instance.response_format = data["response_format"]
        instance.target_structure = data["target_structure"]
        instance.directory_path = data["directory_path"]
        instance.batch_id = data["batch_id"]
        instance.field_name = data["field_name"]

        return instance

    @classmethod
    def load_settings(cls, filepath):
        # Load settings from a JSON file
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return None

        
    def save_settings(self):
        settings_filename = os.path.join(self.directory_path, f"{self.unique_name}_detailssettings.json")
        writeJSON(self.to_dict(), settings_filename)

    
    def __repr__(self):
        return (f"Settings:{self.unique_id},\n {self.unique_name}, {self.model}, "
                f"\nTemperature={self.temperature}, \nTop_p={self.top_p}, "
                f"\nPrompt='{self.prompt}', \nResponse Format='{self.response_format}')")

