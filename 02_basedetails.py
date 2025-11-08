#02_basedetails.py

from details_core import run_details_main
import response_formats


configs = {
    "field_name": "details",
    "response_format_PYDANTIC": response_formats.Details,
    "response_format_TOOLS": response_formats.response_format_tools_vPatientDetails,
    "target_structure_GEN": response_formats.Details_target_structure,
    "tool_choice_name": "patient_details",
    "TEMP_WITH": "02_prompt_details_withResponseFormat.j2",
    "TEMP_WITHOUT": "02_prompt_details_withoutResponseFormat.j2", 
    "information_file": "structured.json",
    "base_path": "../MAIN/data/PatientDatasets/"

}


run_details_main(configs)
