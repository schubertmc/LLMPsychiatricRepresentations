library(strex)
library(pbapply)
library(gtools)
library(patchwork)
library(gridExtra)
library(ComplexHeatmap)
library(dplyr)
library(tidyr)
library(ggplot2)
library(data.table)
library(patchwork)
library(vegan)


# Paths
base_path <-  "../MAIN"
saving_folder <- file.path(base_path, "plots")
saving_tables <- file.path(base_path, "tables")
processed_folder <- file.path(base_path, "data/Processed")
# Paths


# Colorsets #####
colorset  <- c("#c5313c", "#d93173", "#cf7434", "#d93831", "#ae3037", "#8a2724", "#83b454", "#539049", "#2f6d40", "#5aafdc","#34789a", "#215173", "#3f8fbc" )
colorset <- rev(colorset)
bluebrowns  <- c("#ffffff", "#b3ab99", "#d9d4c6", "#ebf1f3", "#8ea9b7")
browns <- c("#ffffff", "#b3ab99", "#d9d4c6")
blues <- c("#395661", "#8ea9b7", "#c1d0d9", "#ebf1f3")
bluebrowns2 <- c( "#395661", "#8ea9b7", "#c1d0d9", "#ebf1f3", "#d9d4c6", "#b3ab99" )
lightyellow <- '#EFE5D5'
yellow <- '#F5CE94'

mental_disorders <- c(
  "Autism spectrum disorders",
  "ADHD",
  "Conduct disorder",                                
  "Eating disorders"  ,
  "Bipolar disorder"    ,
  "Schizophrenia",      
  "Anxiety disorders"    ,                           
  "Depressive disorders"  
)
mental_disorders_short <-c("ASD", 
                           "ADHD", 
                           "CD", 
                           "ED",
                           "BD",
                           "SCZ",
                           "AN",
                           "MDD"
)



variable_mapping <- c(
  "sex"="Sex",
  "smoking" = "Smoking",
  "education" = "Education",
  "employment_status" = "Employment Status",
  "income" = "Income",
  "health_insurance_status" = "Health Insurance Status", 
  "race_ethnicity" = "Race and Ethnicity"
  
)

variables_keys<- c("sex", "smoking", "education", 
                    "employment_status",
                    "income", 
                    "health_insurance_status", 
                    "race_ethnicity"
)

secondary_factors <- list(
  "Sex" = factor(c("Female", "Male"), levels = c("Female", "Male")),
  "Smoking" = factor(c("Never", "Formerly", "Currently"), 
                     levels = c("Never", "Formerly", "Currently")),
  
  "Education" = factor(c("No Formal Education", "Primary School", "Secondary School", "Tertiary School"),
                       levels = c("No Formal Education", "Primary School", "Secondary School", "Tertiary School")),
  
  "Employment Status" = factor( c("Employed", "Self-Employed", "Retired","Student","Other","Unemployed"),
                                levels = c("Employed", "Self-Employed", "Retired","Student","Other","Unemployed" )),
  
  "Income" = factor(c("Low", "Middle", "High"), 
                    levels = c("Low", "Middle", "High")),
  
  "Health Insurance Status" = factor(c("Uninsured", "Public", "Private"), 
                                     levels = c("Uninsured", "Public", "Private")),
  
  "Race and Ethnicity" = factor(c("American Indian Or Alaska Native", "Asian", "Black Or African American", 
                                  "Hispanic Or Latino", "Middle Eastern Or North African", 
                                  "Native Hawaiian Or Pacific Islander", "White"),
                                levels = c("American Indian Or Alaska Native", "Asian", "Black Or African American", 
                                           "Hispanic Or Latino", "Middle Eastern Or North African", 
                                           "Native Hawaiian Or Pacific Islander", "White"))
)

age_groups <- c(
  "<5 years",
  "5-9 years",
  "10-14 years",
  "15-19 years",     
  "20-24 years" ,    
  "25-29 years" , 
  "30-34 years",
  "35-39 years",
  "40-44 years",
  "45-49 years",    
  "50-54 years" ,    
  "55-59 years"  ,
  "60-64 years" ,     
  "65-69 years" ,     
  "70-74 years"  ,    
  "75-79 years" ,     
  "80-84 years" ,   
  "85-89 years" ,     
  "90-94 years",
  "95+ years") 

age_groups_short<- str_remove(age_groups, "ears")
phq9_vector <- c("q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9")

panss_vector <- c(
  "p1_delusions",
  "p2_conceptual_disorganisation",
  "p3_hallucinatory_behaviour",
  "p4_excitement",
  "p5_grandiosity",
  "p6_suspiciousness_persecution",
  "p7_hostility",
  "n1_blunted_affect",
  "n2_emotional_withdrawal",
  "n3_poor_rapport",
  "n4_passive_apathetic_social_withdrawal",
  "n5_difficulty_in_abstract_thinking",
  "n6_lack_of_spontaneity_flow_of_conversation",
  "n7_stereotyped_thinking",
  "g1_somatic_concern",
  "g2_anxiety",
  "g3_guilt_feelings",
  "g4_tension",
  "g5_mannerisms_posturing",
  "g6_depression",
  "g7_motor_retardation",
  "g8_uncooperativeness",
  "g9_unusual_thought_content",
  "g10_disorientation",
  "g11_poor_attention",
  "g12_lack_of_judgement_insight",
  "g13_disturbance_of_volition",
  "g14_poor_impulse_control",
  "g15_preoccupation",
  "g16_active_social_avoidance"
)


panss_map <- data.frame(
  panss_mat_item = c("p1_delusions",
                     "p2_conceptual_disorganisation",
                     "p3_hallucinatory_behaviour",
                     "p4_excitement",
                     "p5_grandiosity",
                     "p6_suspiciousness_persecution",
                     "p7_hostility",
                     "n1_blunted_affect",
                     "n2_emotional_withdrawal",
                     "n3_poor_rapport",
                     "n4_passive_apathetic_social_withdrawal",
                     "n5_difficulty_in_abstract_thinking",
                     "n6_lack_of_spontaneity_flow_of_conversation",
                     "n7_stereotyped_thinking",
                     "g1_somatic_concern",
                     "g2_anxiety",
                     "g3_guilt_feelings",
                     "g4_tension",
                     "g5_mannerisms_posturing",
                     "g6_depression",
                     "g7_motor_retardation",
                     "g8_uncooperativeness",
                     "g9_unusual_thought_content",
                     "g10_disorientation",
                     "g11_poor_attention",
                     "g12_lack_of_judgement_insight",
                     "g13_disturbance_of_volition",
                     "g14_poor_impulse_control",
                     "g15_preoccupation",
                     "g16_active_social_avoidance"),
  zi_item = c("panss_p1_v1",
              "panss_p2_v1",
              "panss_p3_v1",
              "panss_p4_v1",
              "panss_p5_v1",
              "panss_p6_v1",
              "panss_p7_v1",
              "panss_n1_v1",
              "panss_n2_v1",
              "panss_n3_v1",
              "panss_n4_v1",
              "panss_n5_v1",
              "panss_n6_v1",
              "panss_n7_v1",
              "panss_g1_v1",
              "panss_g2_v1",
              "panss_g3_v1",
              "panss_g4_v1",
              "panss_g5_v1",
              "panss_g6_v1",
              "panss_g7_v1",
              "panss_g8_v1",
              "panss_g9_v1",
              "panss_g10_v1",
              "panss_g11_v1",
              "panss_g12_v1",
              "panss_g13_v1",
              "panss_g14_v1",
              "panss_g15_v1",
              "panss_g16_v1")
)


variables <- c( "Education", "Health Insurance Status",
                "Employment Status", "Smoking" ,
                "Income", "Race and Ethnicity"
                
)


# Variables #####


# Functions#####
addNames <- function(list_of_named_dataframes) {
  for (i in 1:length(list_of_named_dataframes)) {
    list_of_named_dataframes[[i]]$df_name <- names(list_of_named_dataframes)[i]
  }
  return(list_of_named_dataframes)
}

format_pvals <- function(p_vals) {
  df <- data.frame(pvals= p_vals, 
                   pstring = p_vals)
  
  df$pstring[df$pvals >0.99] <- ">0.99"
  df$pstring[df$pvals <.0001] <- "<.0001"
  is.na(p_vals)
  df$pstring[df$pvals>=.0001 & df$pvals <=0.99 & !is.na(p_vals)] <- format(round(df$pvals[df$pvals>=.0001 & df$pvals <=0.99 & !is.na(p_vals)], 4), 
                                                                           scientific=F)
  return(df$pstring)
}

# Themes #####
