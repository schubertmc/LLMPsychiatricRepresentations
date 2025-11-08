#file.choose()
library(ggplot2)
source("../MAIN/code/analysis/constants_functions.R")


data <- read.csv("../data/07_Explicit/explicit_information.csv")
data$disorder <- str_before_first(str_after_first(data$disorder, "_"), "_")
data$disorder[data$disorder == "AUT"] <- "ASD"
data$disorder[data$disorder == "BIP"] <- "BD"
data$disorder[data$disorder == "ANX"] <- "AN"


# read in data from llm raun
llm_data <- read.csv(file.path(processed_folder, "main_dataset_v1.csv"))
llm_data <- llm_data %>% 
  filter(llm == "LLM 1")
implicit_summary <- llm_data %>% 
  group_by(group) %>% 
  summarize(implicit_female_pct = 100*sum(sex == "Female", na.rm =T) / n(), 
            implicit_median_age_of_onset = median(age_of_onset,na.rm=T)
            )
explicit_summary <- data %>% 
  group_by(disorder) %>% 
  summarize(mean_explicit_female_pct = mean(female_prevalence_pct), 
            sd = sd(female_prevalence_pct), 
            explicit_median_age_of_onset = mean(median_age_of_onset,na.rm=T)
            )

merged <- merge(implicit_summary, explicit_summary, by.x = "group", by.y= "disorder")
merged$group <- factor(merged$group, mental_disorders_short)


gbd <-read.csv(file.path(processed_folder, "GBD_real_prev_v1.csv"))
all <- merge(gbd, merged, by = "group")

all <- all %>%
  group_by(group) %>%
  mutate(perc_female_gbd = 100 * sum(val[sex_name == "Female"], na.rm = TRUE) / sum(val, na.rm = TRUE))
all_long <- pivot_longer(all, cols = c(implicit_female_pct, mean_explicit_female_pct), names_to = "type", values_to = "female_pct")
all_long$type[all_long$type=="mean_explicit_female_pct"]<- "Explicit"
all_long$type[all_long$type=="implicit_female_pct"]<- "Implicit"
labs_df <- all_long %>%
  group_by(group) %>%
  summarise(
    x = mean(perc_female_gbd, na.rm = TRUE),
    y = mean(female_pct, na.rm = TRUE),
    .groups = "drop"
  )

pright <- ggplot(all_long, aes(x = perc_female_gbd, y = female_pct)) +
  geom_line(data = data.frame(x = 1:100, y = 1:100),
            aes(x, y), color = "grey", inherit.aes = FALSE, linetype="dashed") +
  geom_point(aes(color = type)) +
  geom_path(aes(group = group), color = "darkgrey") +
  ggrepel::geom_text_repel(
    data = labs_df,
    aes(x = x, y = y, label = group), 
    size=2.2
  ) +
  theme_bw() + 
  xlim(20,80) +
  scale_color_manual(values = bluebrowns[c(2,5)],name="" )+
  xlab("Female proportion based on GBD [%]") + 
  ylab("Female proportion based on LLM [%]") +
  theme(legend.position="bottom",
        text = element_text(size = 6.5), 
        plot.title = element_text(size = 7.5))
pright
#ggsave(file.path(saving_folder, "eFigXX_ExplicitvsImplicit_LLM1.png"), width = 5, height = 4, units = "in")



real_inc <- read.csv(file.path(processed_folder, "GBD_real_inc_v1.csv"))
real_inc$age_name_short <- factor(real_inc$age_name_short, levels = age_groups_short)
real_inc$group <- factor(real_inc$group, mental_disorders_short)


# estimate the IQR from the GBD data
estimateIQR <- function(cur_disorder, gbd_data) {
  print(cur_disorder)
  # for real data: 
  # Use Incidence parameters as 'number' of individuals in each age group, calculate percentage each age group represents out of the total cases
  real_inc <- gbd_data %>%
    filter(group == cur_disorder,
           measure_name=="Incidence", 
           metric_name == "Number") %>%
    #group_by(cause_name, age_name) %>%
    #mutate(num_both_sexes = sum(val)) %>% # to add up both sex values
    #filter(sex_name == "Female") %>% # to keep each age category only once
    ungroup() %>% 
    group_by(cause_name) %>%
    mutate(perc =num_both_sexes / sum(num_both_sexes))  %>%  # percentage an age category represents of all cases
    arrange(age_name)
  
  # get 
  real_dist <- real_inc %>% ungroup()%>%
    select(age_name, perc) %>% arrange(age_name)
  real_dist <- setNames(real_dist$perc, real_dist$age_name)
  real_dist <- real_inc %>% ungroup %>% 
    select(age_name, num_both_sexes) %>% arrange(age_name)
  real_dist <- setNames(real_dist$num_both_sexes, real_dist$age_name)
  real_dist_sim <- rep(names(real_dist), round(real_dist))
  real_dist_sim <- factor(real_dist_sim, levels = age_groups)
  real_dist_sim_numeric <- as.numeric(real_dist_sim) * 5 -2.5
  
  quants <- quantile(real_dist_sim_numeric)
  return(quants)
}

iqr_data <- sapply(mental_disorders_short, estimateIQR,gbd_data = real_inc )
t <- t(iqr_data) 
t <- data.frame(t)
t$group <- rownames(t)
iqr_t <- pivot_longer(t, cols = colnames(t)[-6])
iqr_t$name <- str_first_number(iqr_t$name)
iqr_t$name <- dplyr::recode(iqr_t$name,
                                   `25` = "Q1 (25%)",
                                   `50` = "Median (50%)",
                                   `75` = "Q3 (75%)")
iqr_t$name <- factor(iqr_t$name, levels = c("Q1 (25%)","Median (50%)","Q3 (75%)"))


x1 <- ggplot(iqr_t%>%filter(!is.na(name)), aes(x = value, y = group, color = name)) + 
  geom_point(size=0.75)+ 
  theme_bw()+
  xlim(0,100)+
  scale_color_manual(values = bluebrowns2[c(2,5,3)], name="")+
  xlab("Age of Onset")+
  ylab("")+
  ggtitle("GBD") +
  theme(legend.position="bottom",
        text = element_text(size = 6.5), 
        plot.title = element_text(size = 7.5),
        plot.margin = margin(0,0,0,0))
x1  
### 

x2 <- ggplot(data, aes(y = disorder)) +
  theme_bw() +
  geom_jitter(aes(x = iqr_lower,  color = "Q1 (25th %)"),  height = 0.15, size = 0.2) +
  geom_jitter(aes(x = median_age_of_onset, color = "Median (50th %)"), height = 0.15, size = 0.2) +
  geom_jitter(aes(x = iqr_upper,  color = "Q3 (75th %)"),  height = 0.15, size = 0.2) +
  xlim(0, 100) +
  scale_color_manual(
    values = c(
      "Q1 (25th %)" = bluebrowns2[2],
      "Median (50th %)" = bluebrowns2[5],
      "Q3 (75th %)" = bluebrowns2[3]
    ),
    labels = c(
      "Q1" = "Q1 (25th %)",
      "Q2" = "Median (50th %)",
      "Q3" = "Q3 (75th %)"
    ),
    name = ""
  ) +
  xlab("Age of Onset")+
  ylab("")+
  ggtitle("Explicit")+ 
  theme(legend.position="none", 
        text = element_text(size = 6.5), 
        plot.title = element_text(size = 7.5), 
        plot.margin = margin(0,0,0,0))
x2
# llm iqrs
llm_data <-  read.csv(file.path(processed_folder, "main_dataset_v1.csv"))
llm_data <- llm_data %>% 
  filter(llm == "LLM 1")

iqr_llm_impl <- sapply(mental_disorders_short, function(cur_disorder) {
  datx <- llm_data %>%
    filter(group==cur_disorder)
  return(quantile(datx$age_of_onset ,na.rm=T))
})
iqr_llm_impl <- t(iqr_llm_impl)%>% data.frame()
iqr_llm_impl$group <- rownames(iqr_llm_impl)
iqr_llm_impl <- pivot_longer(iqr_llm_impl, cols = colnames(t)[-6])
iqr_llm_impl$name <- str_first_number(iqr_llm_impl$name)
iqr_llm_impl$name <- dplyr::recode(iqr_llm_impl$name,
                                   `25` = "Q1 (25%)",
                                   `50` = "Median (50%)",
                                   `75` = "Q3 (75%)")
iqr_llm_impl$name <- factor(iqr_llm_impl$name, levels = c("Q1 (25%)","Median (50%)","Q3 (75%)"))


x3 <- ggplot(iqr_llm_impl%>%filter(!is.na(name)), aes(x = value, y = group, color = factor(name))) + 
  geom_point(size=0.75)+ 
  theme_bw()+
  scale_color_manual(values = bluebrowns2[c(2,5,3)], name="")+
  
  xlim(0,100)  + 
  xlab("Age of Onset")+
  ylab("")+
  ggtitle("Implicit") + 
  theme(legend.position="none", 
        text = element_text(size = 6.5), 
        plot.title = element_text(size = 7.5), 
        plot.margin = margin(0,0,0,0))


(x3 / x2 / x1) |  pright
ggsave(file.path(saving_folder, "eFig6_ExplicitvsImplicit_IQR_Comb.png"), width = 6, height = 4, units = "in")
 
