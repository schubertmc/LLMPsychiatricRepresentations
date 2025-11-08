# Implicit Representation of Individuals with Mental Disorders in Large Language Models

This repository contains the code used for the study  
**“Implicit Representation of Individuals with Mental Disorders in Large Language Models”**.

The pipeline is organized in two main parts:

- **Part A** – Generation of LLM-derived patient cohorts (Python)
- **Part B** – Analysis and generation of figures and tables (R)

---

## Part A: Generation of LLM Cohorts (Python)

Part A contains all scripts used to query large language models, retrieve patient reports, and construct the analysis-ready datasets.

### 1. Parameter evaluation

Scripts for configuring and testing parameter combinations (parameters, models, prompts):

- `10_run_parameters.py`
- `10B_run_parameters.py`
- `11_run_different_prompts.py`
- `11B_run_different_prompts.py`
- `12_run_different_models.py`
- `12B_run_different_models.py`

### 2. Main cohort generation

Scripts for running the main dataset generation pipeline:

- `01_runDatasetGen.py`
- `01B_retrieveData.py`
- `02_basedetails.py`
- `02B_retrieveData.py`
- `03_details_phq9_panss.py`
- `03B_retrieveData.py`
- `06_buildDataframes_Batch.py`

### 3. Finetuning dataset generation

Scripts for constructing finetuning datasets and running finetuned models:

- `13_datasetgeneration_for_finetuning.py`
- `14_run_finetuned_models.py`

### 4. Supplementary analyses

Scripts for additional analyses reported in the Supplement:

- `21_runDatasetGen_multipleReports.py`
- `21B_retrieveData_multipleReports.py`
- `21C_multipleReports_BuildDataframes.py`
- `22_explicit_knowledge.py`

### 5. Shared modules and utilities

Core helper modules and utilities:

- `response_formats.py`
- `settings_classes.py`
- `apatientreports.py`
- `batch_patientreports.py`
- `details_core.py`
- `utils.py`
- `data_processing.py`
- `code/prompts/` – prompt templates used to query the LLMs

---

## Part B: Analysis and Generation of Plots and Tables (R)

Statistical analyses and figure/table generation are performed in R (folder: `code/analysis/`).

Key scripts:

- `constants_functions.R` – shared constants and helper functions  
- `01_preprocessing.R` – preprocessing of raw Python outputs and data cleaning  
- `02_figures_v5.R` – main figures for the manuscript  
- `03_params_supplementaryanalyses.R` – parameters and functions for supplementary analyses  
- `04_CompareAgeOfOnsetDistributions_v4KSonly.R` – comparison of age-of-onset distributions (KS-based)  
- `21_multipleRuns_analysis.R` – analyses of multiple-generation runs  
- `22_explicitknowledge_v2.R` – analyses of explicit knowledge prompts

### Contact
[Marc Schubert](mailto:marc.schubert@uni-heidelberg.de)