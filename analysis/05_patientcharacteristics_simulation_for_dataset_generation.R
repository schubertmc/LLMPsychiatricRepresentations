library(tidyverse)
library(ggpubr)
source("../code/analysis/constants_functions.R")


#fine_tuning dataset generation
real <- read.csv(file.path(base_path,"data/comps/GBDDATA/IHME-GBD_2021_DATA-c05a1a3b-1.csv"))


table(real$cause_name)

### Functions 
sample_age <- function(age_group) {
  if (age_group == "<5 years") {
    return(sample(0:4, 1))
  } else if (age_group == "95+ years") {
    return(sample(95:100, 1))
  } else {
    lower_bound <- str_first_number_before_first(age_group, "-")
    upper_bound <- str_first_number_after_first(age_group, "-")
    return(sample(lower_bound:upper_bound, 1))
  }
}

############

# age_groups <- c(
#   "<5 years",
#   "5-9 years",
#   "10-14 years",
#   "15-19 years",
#   "20-24 years" ,
#   "25-29 years" ,
#   "30-34 years",
#   "35-39 years",
#   "40-44 years",
#   "45-49 years",
#   "50-54 years" ,
#   "55-59 years"  ,
#   "60-64 years" ,
#   "65-69 years" ,
#   "70-74 years"  ,
#   "75-79 years" ,
#   "80-84 years" ,
#   "85-89 years" ,
#   "90-94 years",
#   "95+ years")
# mental_disorders <- c(
#   # "Mental disorders"
#   # "Other mental disorders",
#   #"Idiopathic developmental intellectual disability"
#   "Autism spectrum disorders",
#   #"Attention-deficit/hyperactivity disorder"   ,
#   "ADHD",
#   "Conduct disorder",
#   "Eating disorders"  ,
#   "Bipolar disorder"    ,
#   "Schizophrenia",
#   "Anxiety disorders"    ,
#   "Depressive disorders"
# )
# real$cause_name[real$cause_name =="Attention-deficit/hyperactivity disorder"] <- "ADHD"
# library(dplyr)
# real$age_name
real <- real %>%
  filter(age_name %in%  age_groups)
real$age_name <- factor(real$age_name, levels = age_groups)
real <- real %>%
  filter(cause_name %in% mental_disorders)
real$disorder <- factor(real$cause_name, levels = mental_disorders)

# Schizophrenia patients only
s <- real %>% 
  filter(cause_name == "Schizophrenia", 
         metric_name == "Number",
         measure_name == "Incidence"
         )
s
ggplot(s,aes(x = age_name, y = val, fill =sex_name )) + 
  geom_bar(stat = "identity", position = "dodge") + 
  theme(axis.text.x = element_text(angle = 45, hjust =1, vjust=1))
#ggsave("Fig_plot_distribution prevalence.png")

s$BIN_ID <- paste0(s$sex_name, "_", s$age_name)
s$perc <- s$val / sum(s$val)

pa <- ggplot(s,aes(x = age_name, y = perc, fill =sex_name )) + 
  theme_bw()+
  geom_bar(stat = "identity", position = "dodge") + 
  ggtitle("GBD 2021") + 
  scale_fill_manual(values = bluebrowns[c(3,5)], name = "Sex") + 
  xlab("Age of Onset") + 
  theme_bw() +
  theme(axis.text.x = element_text(angle = 0, hjust =1, vjust=1, size = 6)) + 
  theme(strip.background = element_blank(),
        strip.text = element_text(face="plain", hjust=0),
        title= element_text(size = 7, face = "bold"),
        text = element_text(size = 7),
        axis.title = element_text(face = "plain"),
        strip.text.x = element_text(face = "plain", size = 8),
        strip.text.y = element_text(face="plain"),
        axis.text.y = element_text(size = 7)  ) + 
  scale_x_discrete(
    breaks = c("25-29 years", "50-54 years", "75-79 years", "100+ years"), # Choose categories to show
    labels = c("25", "50", "75", "100") # Set numeric-like labels
  )

pa
library(strex)
set.seed(123)
data <- sample(s$BIN_ID, 1000,replace = T, prob = s$perc)
data <- data.frame(BIN_ID = data)
data$sex_name <- str_before_first(data$BIN_ID,"_")
data$age_name <- str_after_first(data$BIN_ID,"_")
data$age_name <- factor(data$age_name, levels = age_groups)


set.seed(123)
data$age_exact <- sapply(as.character(data$age_name), sample_age)


data$patient_id <- paste0("SCZ_", 1:nrow(data))
head(data)
#write.csv(data, file.path(base_path, "data/05_Finetuning/Schizophrenia_SimulatedPatientCharacteristics.csv"))



