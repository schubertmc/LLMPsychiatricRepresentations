from pydantic import BaseModel, Field # type: ignore
from typing import Literal
import os 
import uuid
from utils import writeJSON

#### Output formats###
class PatientReport(BaseModel):
    patient_report: str
    class Chars(BaseModel):
        sex: str = Field(description= "M/F") 
        age_current: int
        age_of_onset: int
    chars : Chars


PatientReport_target_structure = {
    "patient_report":str,
    "chars": {
        "sex": str,
        "age_current": int, 
        "age_of_onset":int
    }
}



response_format_tools_vPatientReport = [
        {
            "name": "patient_report",
            "description": "a patient report",
            "input_schema": {
                "type": "object",
                "properties": {

                    "patient_report": {
                        "type": "string",
                        "description": "patient report",
                    },
                    "chars": {
                            "type": "object",
                            "properties": {
                                "sex": {
                                    "type": "string",
                                    "description": "M / F",
                                },
                                "age_current": {
                                    "type": "integer",
                                    "description": "current age <int>",
                                },
                                "age_of_onset": {
                                    "type": "integer",
                                    "description": "age of onset <int>",
                                },
                            },
                            "required": ["sex", "age_current", "age_of_onset"],
                        "description": "chars"
                    }
                },
                "required": ["patient_report", "chars"]
            }
        }
    ]


class Reports(BaseModel):
    reports: list[PatientReport] = []

Reports_target_structure = {
    "reports": [
        {
            "patient_report": str,
            "chars": {
                "sex": str,
                "age_current": int,
                "age_of_onset": int
            }
        }
    ]
}
response_format_tools_Reports = [
        {
            "name": "reports",
            "description": "A list of patient reports",
            "input_schema": {
            "type": "object",
            "properties": {
                "reports": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                    "patient_report": {
                        "type": "string",
                        "description": "patient report"
                    },
                    "chars": {
                        "type": "object",
                        "description": "chars",
                        "properties": {
                        "sex": {
                            "type": "string",
                            "description": "M / F"
                        },
                        "age_current": {
                            "type": "integer",
                            "description": "current age <int>"
                        },
                        "age_of_onset": {
                            "type": "integer",
                            "description": "age of onset <int>"
                        }
                        },
                        "required": ["sex", "age_current", "age_of_onset"]
                    }
                    },
                    "required": ["patient_report", "chars"]
                }
                }
            },
            "required": ["reports"]
            }
        }
]

# Details
class Details(BaseModel):
    BMI: float
    education:str = Field(description="no formal education/primary school/secondary school/tertiary school")
    employment_status:str = Field(description="employed/self-employed/unemployed/retired/student/other")
    income:str = Field(description="low/middle/high")
    health_insurance_status:str = Field(description="public/private/uninsured")
    smoking:str = Field(description = "never/formerly/currently")
    race_ethnicity: Literal[
        "American Indian or Alaska Native",
        "Asian",
        "Black or African American",
        "Hispanic or Latino",
        "Middle Eastern or North African",
        "Native Hawaiian or Pacific Islander",
        "White"
    ] = Field(description="Race and Ethnicity of patient. Choose one of: 'American Indian or Alaska Native', 'Asian', 'Black or African American', 'Hispanic or Latino', 'Middle Eastern or North African', 'Native Hawaiian or Pacific Islander', 'White'.")

    
Details_target_structure = {
    "BMI": float,
    "education": str,
    "employment_status": str,
    "income": str,
    "health_insurance_status": str,
    "smoking": str,
    "race_ethnicity": str
}

response_format_tools_vPatientDetails = [
    {
        "name": "patient_details",
        "description": "Patient demographic and lifestyle details",
        "input_schema": {
            "type": "object",
            "properties": {
                "BMI": {
                    "type": "number",
                    "description": "Body Mass Index of the patient as a float."
                },
                "education": {
                    "type": "string",
                    "description": "Education, options: 'no formal education', 'primary school', 'secondary school', or 'tertiary school'."
                },
                "employment_status": {
                    "type": "string",
                    "description": "Employment status, options: 'employed', 'self-employed', 'unemployed', 'retired', 'student', or 'other'."
                },
                "income": {
                    "type": "string",
                    "description": "Income level, options: 'low', 'middle', or 'high'."
                },
                "health_insurance_status": {
                    "type": "string",
                    "description": "Health insurance status, options: 'public', 'private', or 'uninsured'."
                },
                "smoking": {
                    "type": "string",
                    "description": "Smoking status of the patient, options: 'never', 'formerly', or 'currently'."
                },
                 "race_ethnicity": {
                    "type": "string",
                    "description": (
                        "Race and Ethnicity of patient. Choose one of: 'American Indian or Alaska Native', "
                        "'Asian', 'Black or African American', 'Hispanic or Latino', "
                        "'Middle Eastern or North African', 'Native Hawaiian or Pacific Islander', 'White'."
                    ),
                    "enum": [
                        "American Indian or Alaska Native",
                        "Asian",
                        "Black or African American",
                        "Hispanic or Latino",
                        "Middle Eastern or North African",
                        "Native Hawaiian or Pacific Islander",
                        "White"
                    ],
                },
               
            },
            "required": [
                "BMI",
                "education",
                "employment_status",
                "income",
                "health_insurance_status",
                "smoking",
                "race_ethnicity"

            ],
        }
    }
]


# PHQ9
class PHQ9(BaseModel):
    q1: int = Field(description="Little interest or pleasure in doing things (0-3)")
    q2: int = Field(description="Feeling down, depressed, or hopeless (0-3)")
    q3: int = Field( description="Trouble falling or staying asleep, or sleeping too much (0-3)")
    q4: int = Field( description="Feeling tired or having little energy (0-3)")
    q5: int = Field( description="Poor appetite or overeating (0-3)")
    q6: int = Field( description="Feeling bad about yourself — or that you are a failure or have let yourself or your family down (0-3)")
    q7: int = Field( description="Trouble concentrating on things, such as reading the newspaper or watching television (0-3)")
    q8: int = Field( description="Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual (0-3)")
    q9: int = Field( description="Thoughts that you would be better off dead, or of hurting yourself in some way (0-3)")

PHQ9_target_structure = {
    "q1": int,  # Little interest or pleasure in doing things
    "q2": int,  # Feeling down, depressed, or hopeless
    "q3": int,  # Trouble falling or staying asleep, or sleeping too much
    "q4": int,  # Feeling tired or having little energy
    "q5": int,  # Poor appetite or overeating
    "q6": int,  # Feeling bad about yourself — or that you are a failure or have let yourself or your family down
    "q7": int,  # Trouble concentrating on things, such as reading the newspaper or watching television
    "q8": int,  # Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual
    "q9": int,  # Thoughts that you would be better off dead, or of hurting yourself in some way
}


response_format_tools_PHQ9 = [
    {
        "name": "phq9",
        "description": "Patient Health Questionnaire (PHQ-9) assessment results",
        "input_schema": {
            "type": "object",
            "properties": {
                "q1": {
                    "type": "integer",
                    "description": "Little interest or pleasure in doing things (0-3)",
                },
                "q2": {
                    "type": "integer",
                    "description": "Feeling down, depressed, or hopeless (0-3)",
                },
                "q3": {
                    "type": "integer",
                    "description": "Trouble falling or staying asleep, or sleeping too much (0-3)",
                },
                "q4": {
                    "type": "integer",
                    "description": "Feeling tired or having little energy (0-3)",
                },
                "q5": {
                    "type": "integer",
                    "description": "Poor appetite or overeating (0-3)",
                },
                "q6": {
                    "type": "integer",
                    "description": "Feeling bad about yourself — or that you are a failure or have let yourself or your family down (0-3)",
                },
                "q7": {
                    "type": "integer",
                    "description": "Trouble concentrating on things, such as reading the newspaper or watching television (0-3)",
                },
                "q8": {
                    "type": "integer",
                    "description": "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual (0-3)",
                },
                "q9": {
                    "type": "integer",
                    "description": "Thoughts that you would be better off dead, or of hurting yourself in some way (0-3)",
                },
            },
            "required": ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
        }
    }
]



class PANSS(BaseModel):
    p1_delusions: int = Field(description="Delusions (1-7)")
    p2_conceptual_disorganisation: int = Field(description="Conceptual disorganisation (1-7)")
    p3_hallucinatory_behaviour: int = Field(description="Hallucinatory behaviour (1-7)")
    p4_excitement: int = Field(description="Excitement (1-7)")
    p5_grandiosity: int = Field(description="Grandiosity")
    p6_suspiciousness_persecution: int = Field(description="Suspiciousness/persecution (1-7)")
    p7_hostility: int = Field(description="Hostility (1-7)")
    n1_blunted_affect: int = Field(description="Blunted affect (1-7)")
    n2_emotional_withdrawal: int = Field(description="Emotional withdrawal (1-7)")
    n3_poor_rapport: int = Field(description="Poor rapport (1-7)")
    n4_passive_apathetic_social_withdrawal: int = Field(description="Passive/apathetic social withdrawal (1-7)")
    n5_difficulty_in_abstract_thinking: int = Field(description="Difficulty in abstract thinking (1-7)")
    n6_lack_of_spontaneity_flow_of_conversation: int = Field(description="Lack of spontaneity & flow of conversation (1-7)")
    n7_stereotyped_thinking: int = Field(description="Stereotyped thinking (1-7)")
    g1_somatic_concern: int = Field(description="Somatic concern (1-7)")
    g2_anxiety: int = Field(description="Anxiety (1-7)")
    g3_guilt_feelings: int = Field(description="Guilt feelings (1-7)")
    g4_tension: int = Field(description="Tension")
    g5_mannerisms_posturing: int = Field(description="Mannerisms and posturing (1-7)")
    g6_depression: int = Field(description="Depression (1-7)")
    g7_motor_retardation: int = Field(description="Motor retardation (1-7)")
    g8_uncooperativeness: int = Field(description="Uncooperativeness (1-7)")
    g9_unusual_thought_content: int = Field(description="Unusual thought content (1-7)")
    g10_disorientation: int = Field(description="Disorientation (1-7)")
    g11_poor_attention: int = Field(description="Poor attention (1-7)")
    g12_lack_of_judgement_insight: int = Field(description="Lack of judgement & insight (1-7)")
    g13_disturbance_of_volition: int = Field(description="Disturbance of volition (1-7)")
    g14_poor_impulse_control: int = Field(description="Poor impulse control (1-7)")
    g15_preoccupation: int = Field(description="Preoccupation (1-7)")
    g16_active_social_avoidance: int = Field(description="Active social avoidance (1-7)")


PANSS_target_structure = {
    "p1_delusions": int,  # Delusions
    "p2_conceptual_disorganisation": int,  # Conceptual disorganisation
    "p3_hallucinatory_behaviour": int,  # Hallucinatory behaviour
    "p4_excitement": int,  # Excitement
    "p5_grandiosity": int,  # Grandiosity
    "p6_suspiciousness_persecution": int,  # Suspiciousness/persecution
    "p7_hostility": int,  # Hostility
    "n1_blunted_affect": int,  # Blunted affect
    "n2_emotional_withdrawal": int,  # Emotional withdrawal
    "n3_poor_rapport": int,  # Poor rapport
    "n4_passive_apathetic_social_withdrawal": int,  # Passive/apathetic social withdrawal
    "n5_difficulty_in_abstract_thinking": int,  # Difficulty in abstract thinking
    "n6_lack_of_spontaneity_flow_of_conversation": int,  # Lack of spontaneity & flow of conversation
    "n7_stereotyped_thinking": int,  # Stereotyped thinking
    "g1_somatic_concern": int,  # Somatic concern
    "g2_anxiety": int,  # Anxiety
    "g3_guilt_feelings": int,  # Guilt feelings
    "g4_tension": int,  # Tension
    "g5_mannerisms_posturing": int,  # Mannerisms and posturing
    "g6_depression": int,  # Depression
    "g7_motor_retardation": int,  # Motor retardation
    "g8_uncooperativeness": int,  # Uncooperativeness
    "g9_unusual_thought_content": int,  # Unusual thought content
    "g10_disorientation": int,  # Disorientation
    "g11_poor_attention": int,  # Poor attention
    "g12_lack_of_judgement_insight": int,  # Lack of judgement & insight
    "g13_disturbance_of_volition": int,  # Disturbance of volition
    "g14_poor_impulse_control": int,  # Poor impulse control
    "g15_preoccupation": int,  # Preoccupation
    "g16_active_social_avoidance": int,  # Active social avoidance
}


response_format_tools_PANSS = [
    {
        "name": "panns",
        "description": "Positive and Negative Syndrome Scale (PANSS) assessment results",
        "input_schema": {
            "type": "object",
            "properties": {
                "p1_delusions": {
                    "type": "integer",
                    "description": "Delusions (1-7)",
                },
                "p2_conceptual_disorganisation": {
                    "type": "integer",
                    "description": "Conceptual disorganisation (1-7)",
                },
                "p3_hallucinatory_behaviour": {
                    "type": "integer",
                    "description": "Hallucinatory behaviour (1-7)",
                },
                "p4_excitement": {
                    "type": "integer",
                    "description": "Excitement (1-7)",
                },
                "p5_grandiosity": {
                    "type": "integer",
                    "description": "Grandiosity (1-7)",
                },
                "p6_suspiciousness_persecution": {
                    "type": "integer",
                    "description": "Suspiciousness/persecution (1-7)",
                },
                "p7_hostility": {
                    "type": "integer",
                    "description": "Hostility (1-7)",
                },
                "n1_blunted_affect": {
                    "type": "integer",
                    "description": "Blunted affect (1-7)",
                },
                "n2_emotional_withdrawal": {
                    "type": "integer",
                    "description": "Emotional withdrawal (1-7)",
                },
                "n3_poor_rapport": {
                    "type": "integer",
                    "description": "Poor rapport (1-7)",
                },
                "n4_passive_apathetic_social_withdrawal": {
                    "type": "integer",
                    "description": "Passive/apathetic social withdrawal (1-7)",
                },
                "n5_difficulty_in_abstract_thinking": {
                    "type": "integer",
                    "description": "Difficulty in abstract thinking (1-7)",
                },
                "n6_lack_of_spontaneity_flow_of_conversation": {
                    "type": "integer",
                    "description": "Lack of spontaneity & flow of conversation (1-7)",
                },
                "n7_stereotyped_thinking": {
                    "type": "integer",
                    "description": "Stereotyped thinking (1-7)",
                },
                "g1_somatic_concern": {
                    "type": "integer",
                    "description": "Somatic concern (1-7)",
                },
                "g2_anxiety": {
                    "type": "integer",
                    "description": "Anxiety (1-7)",
                },
                "g3_guilt_feelings": {
                    "type": "integer",
                    "description": "Guilt feelings (1-7)",
                },
                "g4_tension": {
                    "type": "integer",
                    "description": "Tension (1-7)",
                },
                "g5_mannerisms_posturing": {
                    "type": "integer",
                    "description": "Mannerisms and posturing (1-7)",
                },
                "g6_depression": {
                    "type": "integer",
                    "description": "Depression (1-7)",
                },
                "g7_motor_retardation": {
                    "type": "integer",
                    "description": "Motor retardation (1-7)",
                },
                "g8_uncooperativeness": {
                    "type": "integer",
                    "description": "Uncooperativeness (1-7)",
                },
                "g9_unusual_thought_content": {
                    "type": "integer",
                    "description": "Unusual thought content (1-7)",
                },
                "g10_disorientation": {
                    "type": "integer",
                    "description": "Disorientation (1-7)",
                },
                "g11_poor_attention": {
                    "type": "integer",
                    "description": "Poor attention (1-7)",
                },
                "g12_lack_of_judgement_insight": {
                    "type": "integer",
                    "description": "Lack of judgement & insight (1-7)",
                },
                "g13_disturbance_of_volition": {
                    "type": "integer",
                    "description": "Disturbance of volition (1-7)",
                },
                "g14_poor_impulse_control": {
                    "type": "integer",
                    "description": "Poor impulse control (1-7)",
                },
                "g15_preoccupation": {
                    "type": "integer",
                    "description": "Preoccupation (1-7)",
                },
                "g16_active_social_avoidance": {
                    "type": "integer",
                    "description": "Active social avoidance (1-7)",
                },
            },
            "required": [
                "p1_delusions", "p2_conceptual_disorganisation", "p3_hallucinatory_behaviour",
                "p4_excitement", "p5_grandiosity", "p6_suspiciousness_persecution",
                "p7_hostility", "n1_blunted_affect", "n2_emotional_withdrawal",
                "n3_poor_rapport", "n4_passive_apathetic_social_withdrawal",
                "n5_difficulty_in_abstract_thinking", "n6_lack_of_spontaneity_flow_of_conversation",
                "n7_stereotyped_thinking", "g1_somatic_concern", "g2_anxiety",
                "g3_guilt_feelings", "g4_tension", "g5_mannerisms_posturing", "g6_depression",
                "g7_motor_retardation", "g8_uncooperativeness", "g9_unusual_thought_content",
                "g10_disorientation", "g11_poor_attention", "g12_lack_of_judgement_insight",
                "g13_disturbance_of_volition", "g14_poor_impulse_control", "g15_preoccupation",
                "g16_active_social_avoidance"
            ]
        }
    }
]


class Stats(BaseModel):
    median_age_of_onset: float = Field(description="Median age of onset in years")
    iqr_lower: float = Field(description="Lower bound of the IQR (Q1), in years")
    iqr_upper: float = Field(description="Upper bound of the IQR (Q3), in years")
    female_prevalence_pct: float = Field(description="Female prevalence as a percentage (0–100)")


Stats_target_structure = {
    "median_age_of_onset": float,  # Median age of onset in years
    "iqr_lower": float,  # Lower bound of the IQR (Q1), in years
    "iqr_upper": float,  # Upper bound of the IQR (Q3), in years
    "female_prevalence_pct": float,  # Female prevalence as a percentage (0–100)
}

response_format_tools_Stats = [
    {
        "name": "stats",
        "description": "Statistical summary",
        "input_schema": {
            "type": "object",
            "properties": {
                "median_age_of_onset": {
                    "type": "number",
                    "description": "Median age of onset in years",
                },
                "iqr_lower": {
                    "type": "number",
                    "description": "Lower bound of the IQR (Q1), in years",
                },
                "iqr_upper": {
                    "type": "number",
                    "description": "Upper bound of the IQR (Q3), in years",
                },
                "female_prevalence_pct": {
                    "type": "number",
                    "description": "Female prevalence as a percentage (0–100)",
                },
            },
            "required": [
                "median_age_of_onset",
                "iqr_lower",
                "iqr_upper",
                "female_prevalence_pct"
            ]
        }
    }
]