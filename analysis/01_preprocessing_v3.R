#preprocessing.R

source("../MAIN/code/analysis/constants_functions.R")

################# FUNCTIONS END ############### 
################# ############# ############### 

# Preprocessing #####
#LLM Main dataset


setwd(file.path(base_path, "data/04_PatientDatasets"))

files <- c(
  file.path(base_path, "data/04_PatientDatasets/llama/detailed_quants_bound_structured_withDetails.json.csv"),
  file.path(base_path, "data/04_PatientDatasets/anthropic/detailed_quants_bound_structured_withDetails.json.csv"),
  file.path(base_path, "data/04_PatientDatasets/openai/detailed_quants_bound_structured_withDetails.json.csv")
)

data <- pblapply(files, fread)
names(data) <- files
data <- addNames(data)
cols <- lapply(data, colnames)

data <- do.call("smartbind", data)

data$llm <- str_before_first(data$json_file, "_")
data$llm[data$llm=="openai"] <- "LLM 1"
data$llm[data$llm=="anthropic"] <- "LLM 2"
data$llm[data$llm=="llama"] <- "LLM 3"

data$group <- str_before_first(str_after_first(data$json_file, "_"), "_")
data$group[data$group == "AUT"] <- "ASD"
data$group[data$group == "BIP"] <- "BD"
data$group[data$group == "ANX"] <- "AN"
data$group <- factor(data$group, mental_disorders_short)
unique(data$group)
data$age_of_onset[data$age_of_onset<0] <- NA


#

# Cleaning variables
bx <- paste0(data$llm, data$sex)
bx <- data$sex
table(bx) %>%data.frame()%>% arrange(-Freq)
data$sex[data$sex=="M"] <- "Male"
data$sex[data$sex=="F"] <- "Female"
data$sex <- factor(data$sex, levels = c("Female", "Male"))
data$age_of_onset <- as.numeric(data$age_of_onset)

# counting freqs
freqs <- pblapply(c("sex", variables_keys), function(key) {
  freq <- table(str_to_title(data[,key])) %>% data.frame() %>%arrange(-Freq)
  freq$key <- key
  freq <- relocate(freq, c(key, Freq))
  return(freq)
})


for (key in variables_keys) {
  print(key)
  data[,key] <- str_to_title(data[,key])
  data[,key] <- factor(data[,key], levels = levels(secondary_factors[[variable_mapping[[key]]]]) )
}

long <- pivot_longer(data, cols = all_of(variables_keys))
long <- long %>%
  mutate(name_long = variable_mapping[name])


write.csv(data,file.path(processed_folder, "main_dataset_v1.csv"))
write.csv(long,file.path(processed_folder, "long_dataset_v1.csv"))



# pansss and etc 
files  <-c( file.path(base_path, "data/04_PatientDatasets/anthropic/detailed_quants_bound_structured_withDetails_V2.json.csv"), 
            file.path(base_path, "data/04_PatientDatasets/openai/detailed_quants_bound_structured_withDetails_V2.json.csv"), 
            file.path(base_path, "data/04_PatientDatasets/llama/detailed_quants_bound_structured_withDetails_V2.json.csv")
)

data <- pblapply(files, fread)
names(data) <- files
data <- addNames(data)
cols <- lapply(data, colnames)

data <- do.call("smartbind", data)
data$llm <- str_before_first(data$json_file, "_")
data$group <- str_before_first(str_after_first(data$json_file, "_"), "_")
data$group <- factor(data$group, mental_disorders_short)
data$llm[data$llm=="openai"] <- "LLM 1"
data$llm[data$llm=="anthropic"] <- "LLM 2"
data$llm[data$llm=="llama"] <- "LLM 3"

write.csv(data,file.path(processed_folder, "PHQ9_PANSS_combined.csv"))

data$q_sum <- rowSums(data[,phq9_vector])


phq9_mat <- data[,phq9_vector]
rownames(phq9_mat) <- data$rid
target_bool <- rowSums(is.na(phq9_mat))<5
phq9_mat <- phq9_mat[target_bool,]

# filter out with too high max vals
max_vals <- apply(phq9_mat, 1, max)
table(max_vals)
table(max_vals<=3)
phq9_mat <- phq9_mat[max_vals<=3,]
dim(phq9_mat)

# filter out too low min vals
min_vals <- apply(phq9_mat, 1, min)
phq9_mat <- phq9_mat[min_vals>=0,]
table(min_vals>=0)

write.csv(phq9_mat,file.path(processed_folder, "phq_9_mat_v1.csv"))




panss_mat <- data[,panss_vector]
rownames(panss_mat) <- data$rid
target_bool <- rowSums(is.na(panss_mat))<5
panss_mat <- panss_mat[target_bool,]

# filter out with too high max vals
max_vals <- apply(panss_mat, 1, max)
table(max_vals)
table(max_vals<=7)
panss_mat <- panss_mat[max_vals<=7,]
dim(panss_mat)

# filter out too low min vals
min_vals <- apply(panss_mat, 1, min)
table(min_vals)
panss_mat <- panss_mat[min_vals>=1,]
table(min_vals>=1)


write.csv(panss_mat,file.path(processed_folder, "panss_mat_v1.csv"))



# GBD Data
real <- read.csv(file.path(base_path,"data/comps/GBDDATA/IHME-GBD_2021_DATA-c05a1a3b-1.csv"))


real$gbd <- "GBD 2021"
table(real$cause_name)
unique(real$cause_name)
real$disorder <- real$cause_name
real$group <- as.character(real$disorder)
real$group[real$group == "Anxiety disorders"] <- "AN"
real$group[real$group == "Autism spectrum disorders"] <- "ASD"
real$group[real$group == "ADHD"] <- "ADHD"
real$group[real$group == "Attention-deficit/hyperactivity disorder"] <- "ADHD"
real$group[real$group == "Conduct disorder"] <- "CD"
real$group[real$group == "Eating disorders"] <- "ED"
real$group[real$group == "Bipolar disorder"] <- "BD"
real$group[real$group == "Schizophrenia"] <- "SCZ"
real$group[real$group == "Anxiety disorders"] <- "AN"
real$group[real$group == "Depressive disorders"] <- "MDD"
real$group <- factor(real$group, mental_disorders_short)
table(real$group)
real$age_name_short <- str_remove(real$age_name, "ears")
real$age_name_short <- factor(real$age_name_short, levels = age_groups_short)

real_inc <- real %>% 
  filter(age_name %in% age_groups)%>%
  filter(measure_name=="Incidence", 
         metric_name == "Number", 
  ) %>%
  group_by(group, age_name) %>%
  mutate(num_both_sexes = sum(val), 
         num_both_sexes_upper = sum(upper), 
         num_both_sexes_lower = sum(lower)
         ) %>%
  filter(sex_name == "Female") %>% # to just keep both sexes values
  ungroup()%>% 
  group_by(group) %>%
  mutate(perc =num_both_sexes / sum(num_both_sexes),
         perc_upper = num_both_sexes_upper / sum(num_both_sexes), 
         perc_lower = num_both_sexes_lower / sum(num_both_sexes)
         ) %>%
  filter(!is.na(group))

write.csv(real_inc,file.path(processed_folder, "GBD_real_inc_v1.csv"))



# GBD prevalence
gbd <- read.csv(file.path(base_path,"data/comps/GBDDATA/IHME-GBD_2021_DATA-c05a1a3b-1.csv"))
gbd$cause_name[gbd$cause_name =="Attention-deficit/hyperactivity disorder"] <- "ADHD"
table(gbd$age_name)
table(gbd$measure_name)
#View(gbd)
gbd <- gbd %>%
  filter(measure_name == "Prevalence", 
         age_name == "All ages"
  )
gbd <- gbd %>% 
  filter(         metric_name == "Number") # Previously percent
gbd$cause_name <- factor(gbd$cause_name, levels = mental_disorders)

gbd$group <- as.character(gbd$cause_name)
gbd$group[gbd$group == "Anxiety disorders"] <- "AN"
gbd$group[gbd$group == "Autism spectrum disorders"] <- "ASD"
gbd$group[gbd$group == "ADHD"] <- "ADHD"
gbd$group[gbd$group == "Attention-deficit/hyperactivity disorder"] <- "ADHD"
gbd$group[gbd$group == "Conduct disorder"] <- "CD"
gbd$group[gbd$group == "Eating disorders"] <- "ED"
gbd$group[gbd$group == "Bipolar disorder"] <- "BD"
gbd$group[gbd$group == "Schizophrenia"] <- "SCZ"
gbd$group[gbd$group == "Anxiety disorders"] <- "AN"
gbd$group[gbd$group == "Depressive disorders"] <- "MDD"
gbd$group <- factor(gbd$group, mental_disorders_short)

gbd$sex <- gbd$sex_name
gbd$sex <- factor(gbd$sex, levels = c("Female", "Unknown", "Male"))
gbd$llm <- "GBD 2021"

write.csv(gbd,file.path(processed_folder, "GBD_real_prev_v1.csv"))








# usa
real <- read.csv("../GBDDATA/USA_IHME-GBD_2021_DATA-ce174afd-1.csv")

real$gbd <- "GBD 2021"
table(real$cause_name)
unique(real$cause_name)
real$disorder <- real$cause_name
real$group <- as.character(real$disorder)
real$group[real$group == "Anxiety disorders"] <- "AN"
real$group[real$group == "Autism spectrum disorders"] <- "ASD"
real$group[real$group == "ADHD"] <- "ADHD"
real$group[real$group == "Attention-deficit/hyperactivity disorder"] <- "ADHD"
real$group[real$group == "Conduct disorder"] <- "CD"
real$group[real$group == "Eating disorders"] <- "ED"
real$group[real$group == "Bipolar disorder"] <- "BD"
real$group[real$group == "Schizophrenia"] <- "SCZ"
real$group[real$group == "Anxiety disorders"] <- "AN"
real$group[real$group == "Depressive disorders"] <- "MDD"
real$group <- factor(real$group, mental_disorders_short)
table(real$group)
real$age_name_short <- str_remove(real$age_name, "ears")
real$age_name_short <- factor(real$age_name_short, levels = age_groups_short)

real_inc <- real %>%
  filter(age_name %in% age_groups)%>%
  filter(measure_name=="Incidence",
         metric_name == "Number",
  ) %>%
  group_by(group, age_name) %>%
  mutate(num_both_sexes = sum(val),
         num_both_sexes_upper = sum(upper),
         num_both_sexes_lower = sum(lower)
  ) %>%
  filter(sex_name == "Female") %>% # to just keep both sexes values
  ungroup()%>%
  group_by(group) %>%
  mutate(perc =num_both_sexes / sum(num_both_sexes),
         perc_upper = num_both_sexes_upper / sum(num_both_sexes),
         perc_lower = num_both_sexes_lower / sum(num_both_sexes)
  ) %>%
  filter(!is.na(group))

write.csv(real_inc,file.path(processed_folder, "USA_GBD_real_inc_v1.csv"))




# GBD prevalence
gbd <- read.csv("../GBDDATA/USA_IHME-GBD_2021_DATA-ce174afd-1.csv")
gbd$cause_name[gbd$cause_name =="Attention-deficit/hyperactivity disorder"] <- "ADHD"
table(gbd$age_name)
table(gbd$measure_name)
#View(gbd)
gbd <- gbd %>%
  filter(measure_name == "Prevalence", 
         age_name == "All ages"
  )
gbd <- gbd %>% 
  filter(         metric_name == "Number") # Previously percent
gbd$cause_name <- factor(gbd$cause_name, levels = mental_disorders)

gbd$group <- as.character(gbd$cause_name)
gbd$group[gbd$group == "Anxiety disorders"] <- "AN"
gbd$group[gbd$group == "Autism spectrum disorders"] <- "ASD"
gbd$group[gbd$group == "ADHD"] <- "ADHD"
gbd$group[gbd$group == "Attention-deficit/hyperactivity disorder"] <- "ADHD"
gbd$group[gbd$group == "Conduct disorder"] <- "CD"
gbd$group[gbd$group == "Eating disorders"] <- "ED"
gbd$group[gbd$group == "Bipolar disorder"] <- "BD"
gbd$group[gbd$group == "Schizophrenia"] <- "SCZ"
gbd$group[gbd$group == "Anxiety disorders"] <- "AN"
gbd$group[gbd$group == "Depressive disorders"] <- "MDD"
gbd$group <- factor(gbd$group, mental_disorders_short)

gbd$sex <- gbd$sex_name
gbd$sex <- factor(gbd$sex, levels = c("Female", "Unknown", "Male"))
gbd$llm <- "GBD 2021"

write.csv(gbd,file.path(processed_folder, "USA_GBD_real_prev_v1.csv"))

