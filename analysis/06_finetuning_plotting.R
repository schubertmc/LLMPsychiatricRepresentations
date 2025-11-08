library(tidyverse)
library(ggpubr)
source("../MAIN/code/analysis/constants_functions.R")


#fine_tuning dataset generation
real <- read.csv(file.path(base_path,"data/comps/GBDDATA/IHME-GBD_2021_DATA-c05a1a3b-1.csv"))

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


data <- read.csv(file.path(base_path, "data/05_Finetuning/Schizophrenia_SimulatedPatientCharacteristics.csv"))
data$age_name <- factor(data$age_name, levels = age_groups)



pc <- ggplot(data, aes(x = age_exact, fill = sex_name)) + 
  geom_histogram(position ="dodge", bins = 20) + 
  ggtitle("Simulated")
pb <- ggplot(data, aes(x = age_name, fill = sex_name)) + 
  theme_bw()+
  geom_bar(stat = "count", position ="dodge") + 
  theme(axis.text.x = element_text(angle = 45, hjust =1, vjust=1)) + 
  scale_fill_manual(values = bluebrowns[c(3,5)], name = "Sex")+
  ggtitle("Simulated Training Dataset") + 
  xlab("Age of Onset") + 
  theme_bw() +
  theme(axis.text.x = element_text(angle = 0, hjust =1, vjust=1, size = 6)) + 
  theme(strip.background = element_blank(),
        strip.text = element_text(face="plain", hjust=0),
        title= element_text(size = 7, face = "bold"),
        axis.title = element_text(face = "plain"),
        text = element_text(size = 7),
        strip.text.x = element_text(face = "plain", size = 8),
        strip.text.y = element_text(face="plain"),
        axis.text.y = element_text(size = 7)  )+
  scale_x_discrete(
    breaks = c("25-29 years", "50-54 years", "75-79 years", "100+ years"), # Choose categories to show
    labels = c("25", "50", "75", "100"), 
    drop=F
    # Set numeric-like labels
  ) 

pb
# read in data 
base <- file.path(base_path, "data/05_Finetuning/base_schizo_1000_vA_e118a595912c4835ae0a7bb923fb17da/quants.csv")
finetuned <- file.path(base_path, "data/05_Finetuning/finetuned_run_schizo_epoch3_9fe57efda5be4e37b3b72543ba91b3f8/quants.csv")
finetuned_epoch8 <- file.path(base_path, "data/05_Finetuning/finetuned_run_schizo_epoch8_57dc64fcac7c4882987ebf52a7c3b072/quants.csv")
finetuned_epoch12 <- file.path(base_path, "data/05_Finetuning/finetuned_run_schizo_epoch12_4fbb940fb6ad413fab636cb053f4ad7c/quants.csv")
ft <- read.csv(finetuned)
base <- read.csv(base)
ft2 <- read.csv(finetuned_epoch8)
ft12 <- read.csv(finetuned_epoch12)
pa/pb

base$group <- "Base Model (LLM 1)"
ft$group <- "Finetuned (Ep 3)"
ft2$group <- "Finetuned (Ep 8)"
ft12$group <- "Finetuned (Ep 12)"
colnames(base)[2] <- "sex"
all <- rbind(base, ft, ft2, ft12)
all$id <- ""
all$group <- factor(all$group, levels = c("Base Model (LLM 1)", "Finetuned (Ep 3)",  "Finetuned (Ep 8)",  "Finetuned (Ep 12)" ))
all$sex[all$sex=="F"] <- "Female"
all$sex[all$sex=="M"] <- "Male"

p_others <- ggplot(all, aes(x = age_of_onset, fill = sex)) + 
  theme_bw() + 
    geom_histogram(position = "dodge") + 
  xlim(c(0,100)) + 
  scale_fill_manual(values = bluebrowns[c(3,5)], name = "Sex")+
  facet_wrap(~group, scales = "free",  ncol = 1) + 
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text = element_text(face="plain", hjust=0),
        title= element_text(size = 7, face = "plain"),
        text = element_text(size = 6),
        strip.text.x = element_text(face = "bold", size = 8),
        strip.text.y = element_text(face="bold"),
        axis.text.x = element_text(size = 6),
        #axis.text.y = element_text(size = 7)  
        ) + 
  xlab("Age of Onset")

ggarrange(pa,pb, p_others, ncol=2, nrow=2)

empty_plot <- ggplot() + theme_void()
p_ab_stack <- (pa+theme(legend.position="none", 
                        plot.title = element_text(vjust=-8)
                        ))/(pb+theme(legend.position="none"))/empty_plot/empty_plot + plot_layout(heights = c(1,1,2,1))

p_ab_stack  | p_others

ggsave(file.path(saving_folder, "Fig5_Finetuning.png"), width = 6, height =5, units = "in")




