source("../MAIN/code/analysis/constants_functions.R")

files <- c(
  file.path(base_path, "data/06_MultReps/anthropic/detailed_quants_bound_structured.json.csv"),
  file.path(base_path, "data/06_MultReps/openai/detailed_quants_bound_structured.json.csv"), 
  file.path(base_path, "data/06_MultReps/llama/detailed_quants_bound.csv")
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
data$age_of_onset[data$age_of_onset<0] <- NA

data$sex[data$sex=="M"] <- "Male"
data$sex[data$sex=="F"] <- "Female"
data$sex <- factor(data$sex, levels = c("Female", "Male"))
data$group_merged <- paste(data$group,"-", data$llm)
data <- data %>% group_by(group_merged) %>% 
  mutate(index=row_number())

# generate figure; 
# Figure 1 - basic data
pa <-ggplot(data 
         , aes(x = age_of_onset, fill = llm)) + 
  geom_histogram(aes(y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]),
                 bins = 25, color = "grey40", size = 0.2) + 
  xlim(0,100)+
  facet_grid(llm~group, 
             scales = "fixed", switch="y")+
  scale_fill_manual(values = blues)+
  
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text = element_text(face="plain", hjust=0),
  ) +
  xlab("Age of Onset") +
  ylab("[%]")  +
  theme(title= element_text(size = 7, face = "plain"),
        text = element_text(size = 7),
        strip.text.x = element_text(face = "bold", size = 9),
        strip.text.y = element_text(face="bold", size=7),
        axis.text.x = element_text(size = 7),
        axis.text.y = element_text(size = 7), 
        legend.position = "none"
  )

pa

pb <- ggplot(data %>%
         filter(group %in% mental_disorders_short)
       , aes(y = llm, fill = sex)) + 
  geom_bar(position = "fill") + 
  facet_wrap(~group, ncol = 8)+
  scale_fill_manual(values = c(bluebrowns[5], bluebrowns[3]), name = "Sex")+
  theme_bw() +
  xlab("")+
  ylab("")+
  theme(strip.background = element_blank(),
        strip.text = element_text(face="plain", hjust=0),
        title= element_text(size = 7, face = "plain"),
        text = element_text(size = 7),
        strip.text.x = element_text(face = "bold", size = 9),
        strip.text.y = element_text(face="bold"),
        axis.text.x = element_text(size = 7),
        axis.text.y = element_text(size = 7, face="bold"),
        legend.key.size = unit(0.4, "cm")
  )+
  scale_x_continuous(labels = function(x) x *100)

pa / pb + plot_layout(heights = c(5,1))
#ggsave(file.path(saving_folder, "FigX_Age_and_Sex_MultRuns.png"), width = 11, height = 5, units = "in")

# Figure B - oscillating patterns

pc <- ggplot(data, aes(x = index, age_of_onset)) + 
  theme_bw()+
  geom_vline(xintercept=20, color = "grey")+
  geom_vline(xintercept=40, color = "grey")+
  geom_vline(xintercept=60, color = "grey")+
  geom_vline(xintercept=80, color = "grey")+
  geom_line()+
  facet_wrap(~group_merged, 
             scales = "free", ncol = 3) + 
  ylab("Age of Onset") + 
  theme(strip.background = element_blank(),
        strip.text = element_text(face="plain", hjust=0),
        title= element_text(size = 7, face = "plain"),
        text = element_text(size = 7),
        strip.text.x = element_text(face = "bold", size = 9),
        strip.text.y = element_text(face="bold"),
        axis.text.x = element_text(size = 7),
        axis.text.y = element_text(size = 7, face="bold"),
        legend.key.size = unit(0.4, "cm")
  ) + 
  geom_point(aes(color = sex), size = 0.3) +   scale_color_manual(values = c(bluebrowns[5], bluebrowns[2]), name = "Sex")


pa / pb  / pc + plot_layout(heights = c(2,0.5, 4)) + plot_annotation(tag_levels = list(c('A', ' ', "B", " "))) & theme(plot.tag = element_text(face = 'bold'))
ggsave(file.path(saving_folder, "eFig5_Age_and_Sex_MultRuns.png"), width = 8.5, height = 11, units = "in")


# Statiscial Comparisons
gbd_data_global <- read.csv(file.path(processed_folder, "GBD_real_inc_v1.csv"))

# Filter out other age groups such as 'all ages'
gbd_data_global <- gbd_data_global %>% 
  filter(age_name %in% age_groups)
gbd_data_global$age_name <- factor(gbd_data_global$age_name, levels = age_groups)
gbd_data_usa <- gbd_data_usa %>% 
  filter(age_name %in% age_groups)
gbd_data_usa$age_name <- factor(gbd_data_usa$age_name, levels = age_groups)

llm_data <- data
compareDistributionsKS <- function(cur_disorder, gbd_data) {
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
  real_inc
  # get 
  real_dist <- real_inc %>% ungroup()%>%
    select(age_name, perc) %>% arrange(age_name)
  real_dist <- setNames(real_dist$perc, real_dist$age_name)
  real_dist <- real_inc %>% ungroup %>% 
    select(age_name, num_both_sexes) %>% arrange(age_name)
  real_dist <- setNames(real_dist$num_both_sexes, real_dist$age_name)
  
  
  
  llm_list <- c("LLM 1", "LLM 2", "LLM 3")
  ad_results <- lapply(llm_list, function(llm_name) {
    print(llm_name)
    llm <- llm_data %>%
      filter(group == cur_disorder,
             llm == llm_name
      ) %>%arrange(age_of_onset)
    # assign values to bins, equivalent to GBD data
    
    
    
    llm$age_group <- cut(llm$age_of_onset, breaks = c(seq(0, 100, 5)), labels = age_groups)
    llm$age_group_numeric <- as.numeric(llm$age_group) * 5 -2.5
    
    real_dist_sim <- rep(names(real_dist), round(real_dist))
    real_dist_sim <- factor(real_dist_sim, levels = age_groups)
    real_dist_sim_numeric <- as.numeric(real_dist_sim) * 5 -2.5
    
    #make_sample <- function(pmf, x_vals, n = 10000) {
    #  sample(x_vals, size = n, replace = TRUE, prob = pmf)
    #}
    
    #  set.seed(123)
    #ages_real <- make_sample(real_dist, x_vals = seq(2.5, 97.5, by = 5))
    #ks_result <- ks.test(ages_real, llm$age_group_numeric)
    
    
    ks_result <- ks.test(real_dist_sim_numeric, llm$age_group_numeric)
    
    
    ####ks_result <- ks.test(llm_counts_obs/sum(llm_counts_obs), real_dist)
    
    df <- data.frame(disorder = cur_disorder,
                     llm = llm_name,
                     ks_test_stat_D = ks_result$statistic[[1]],
                     ks_test_p_value = ks_result$p.value[[1]]
    )
    return(df)
    
  })  
  
  ad_results <- do.call("rbind", ad_results)
  
  return(ad_results)  
}

# global
all_comps <- lapply(mental_disorders_short, compareDistributionsKS, gbd_data = gbd_data_global)
all_comps <- do.call("rbind", all_comps)
head(all_comps)
all_comps$ks_test_p_value <- p.adjust(all_comps$ks_test_p_value, "BH")

all_comps <- rename(all_comps, 
                    ks_test_p_value_adj=ks_test_p_value
)
all_comps$ks_test_p_value_adj <- format_pvals(all_comps$ks_test_p_value_adj)

#all_comps$ks_test_stat_D <- 
write.csv(all_comps, file.path(saving_tables,"eTable8_AgeofOnset_MultAtOnce_KS_Global.csv"))


# chisquare tests regarding the sex distributions
gbd_prev_global <- read.csv(file.path(processed_folder, "GBD_real_prev_v1.csv"))

compareSexChisq <- function(cur_disorder, gbd_prev ) {
  
  print(cur_disorder)
  # for real data: 
  # Use Incidence parameters as 'number' of individuals in each age group, calculate percentage each age group represents out of the total cases
  prev <- gbd_prev %>%
    filter(group == cur_disorder,
           measure_name=="Prevalence", 
           metric_name == "Number")  %>%
    mutate(num_both_sexes = sum(val), 
           perc_sex = val / num_both_sexes
    )
  
  
  llm_list <- c("LLM 1", "LLM 2", "LLM 3")
  chi_results <- lapply(llm_list, function(llm_name) {
    print(llm_name)
    llm <- llm_data %>%
      filter(group == cur_disorder, 
             llm == llm_name
      ) %>%group_by(sex) %>% 
      summarize(n =n()) %>% 
      filter(!is.na(sex))
    
    n_total <-sum(llm$n)
    print(n_total)
    sex_matrix <- matrix(c(prev$perc_sex[prev$sex_name=="Female"]*n_total, prev$perc_sex[prev$sex_name=="Male"]*n_total, 
                           llm$n[llm$sex == "Female"], llm$n[llm$sex == "Male"]), nrow=2, byrow = T)
    print(sex_matrix)
    
    
    cramers_v <- rcompanion::cramerV(sex_matrix)[[1]]
    
    res <-chisq.test(sex_matrix)
    df <- data.frame(disorder = cur_disorder,
                     llm = llm_name,
                     X_squared = res$statistic,
                     llm_perc_female = llm$n[llm$sex == "Female"]/n_total, 
                     gbd_perc_female = prev$perc_sex[prev$sex_name=="Female"],
                     p_value = res$p.value, 
                     cramers_v = cramers_v
    )
    return(df)
    
  })
  
  
  chi_results <- do.call("rbind", chi_results)
  
  return(chi_results)
  
}

# global
all_chisqs <- lapply(mental_disorders_short, compareSexChisq, gbd_prev = gbd_prev_global)
all_chisqs <- do.call("rbind", all_chisqs)

quantile(all_chisqs$llm_perc_female) %>% write.csv(file.path(saving_tables, "OTHER_IQR_female_ratio_mult.csv"))


all_chisqs$gbd_perc_female <- as.character(round(all_chisqs$gbd_perc_female, 4)*100)
all_chisqs$llm_perc_female <- as.character(round(all_chisqs$llm_perc_female, 4)*100)
all_chisqs$X_squared <- as.character(round(all_chisqs$X_squared, 2))
all_chisqs$p_value <- p.adjust(all_chisqs$p_value, method = "BH")
all_chisqs <- rename(all_chisqs, p_value_adj = p_value)

all_chisqs$p_value_adj <- format_pvals(all_chisqs$p_value_adj)

write.csv(all_chisqs, file.path(saving_tables, "eTable9_Sex_Distribution_MultAtOnce_Comparison-X-squared_Global.csv"))




