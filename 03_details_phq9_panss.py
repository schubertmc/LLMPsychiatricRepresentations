#03details_phq9.py

from details_core import run_details_main
import response_formats


# PHQ9
configs = {
    "field_name": "PHQ9",
    "response_format_PYDANTIC": response_formats.PHQ9,
    "response_format_TOOLS": response_formats.response_format_tools_PHQ9,
    "target_structure_GEN": response_formats.PHQ9_target_structure,
    "tool_choice_name": "phq9",
    "TEMP_WITH": "04_prompt_phq_9_withResponseFormat.j2",
    "TEMP_WITHOUT": "04_prompt_phq_9_withResponseFormat.j2", 
    "information_file": "structured_withDetails.json",
    "base_path": "../MAIN/data/PatientDatasets/"
}


run_details_main(configs, filter="MDD")



# PANSS
configs = {
    "field_name": "PANSS",
    "response_format_PYDANTIC": response_formats.PANSS,
    "response_format_TOOLS": response_formats.response_format_tools_PANSS,
    "target_structure_GEN": response_formats.PANSS_target_structure,
    "tool_choice_name": "panns",
    "TEMP_WITH": "05_prompt_panss_withResponseFormat.j2",
    "TEMP_WITHOUT": "05_prompt_panss_withResponseFormat.j2", 
    "information_file": "structured_withDetails.json",
    "base_path": "../MAIN/data/PatientDatasets/"
}


run_details_main(configs, filter="SCZ")
