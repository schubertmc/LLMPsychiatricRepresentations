# comparison of real GBD dataset with LLM data

source("../MAIN/code/analysis/constants_functions.R")

gbd_data_global <- read.csv(file.path(processed_folder, "GBD_real_inc_v1.csv"))
gbd_data_usa <- read.csv(file.path(processed_folder, "USA_GBD_real_inc_v1.csv"))

llm_data <- read.csv(file.path(processed_folder, "main_dataset_v1.csv"))


# Filter out other age groups such as 'all ages'
gbd_data_global <- gbd_data_global %>% 
    filter(age_name %in% age_groups)
gbd_data_global$age_name <- factor(gbd_data_global$age_name, levels = age_groups)
gbd_data_usa <- gbd_data_usa %>% 
  filter(age_name %in% age_groups)
gbd_data_usa$age_name <- factor(gbd_data_usa$age_name, levels = age_groups)

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

 write.csv(all_comps, file.path(saving_tables,"eTable3_AgeofOnset_Distributions_KS_Global.csv"))


#usa
all_comps <- lapply(mental_disorders_short, compareDistributionsKS, gbd_data = gbd_data_usa)
all_comps <- do.call("rbind", all_comps)
head(all_comps)
all_comps$ks_test_p_value <- p.adjust(all_comps$ks_test_p_value, "BH")

all_comps <- rename(all_comps, 
                    ks_test_p_value_adj=ks_test_p_value
)

all_comps$ks_test_p_value_adj <- format_pvals(all_comps$ks_test_p_value_adj)

write.csv(all_comps, file.path(saving_tables,"eTable5_AgeofOnset_Distributions_KS_USA.csv"))



# chisquare tests regarding the sex distributions
gbd_prev_global <- read.csv(file.path(processed_folder, "GBD_real_prev_v1.csv"))
gbd_prev_usa <- read.csv(file.path(processed_folder, "USA_GBD_real_prev_v1.csv"))

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

all_chisqs$gbd_perc_female <- as.character(round(all_chisqs$gbd_perc_female, 4)*100)
all_chisqs$llm_perc_female <- as.character(round(all_chisqs$llm_perc_female, 4)*100)
all_chisqs$X_squared <- as.character(round(all_chisqs$X_squared, 2))
all_chisqs$p_value <- p.adjust(all_chisqs$p_value, method = "BH")
all_chisqs <- rename(all_chisqs, p_value_adj = p_value)

all_chisqs$p_value_adj <- format_pvals(all_chisqs$p_value_adj)
write.csv(all_chisqs, file.path(saving_tables, "eTable4_Sex_Distribution_Comparison-X-squared_Global.csv"))


#usa
all_chisqs <- lapply(mental_disorders_short, compareSexChisq, gbd_prev = gbd_prev_usa)
all_chisqs <- do.call("rbind", all_chisqs)

all_chisqs$gbd_perc_female <- as.character(round(all_chisqs$gbd_perc_female, 4)*100)
all_chisqs$llm_perc_female <- as.character(round(all_chisqs$llm_perc_female, 4)*100)
all_chisqs$X_squared <- as.character(round(all_chisqs$X_squared, 2))
all_chisqs$p_value <- p.adjust(all_chisqs$p_value, method = "BH")
all_chisqs <- rename(all_chisqs, p_value_adj = p_value)

all_chisqs$p_value_adj <- format_pvals(all_chisqs$p_value_adj)
write.csv(all_chisqs, file.path(saving_tables, "eTable6_Sex_Distribution_Comparison-X-squared_USA.csv"))




## Compare Finetuning distributions 
finetuned <- file.path(base_path, "data/05_Finetuning/finetuned_run_schizo_epoch3_9fe57efda5be4e37b3b72543ba91b3f8/quants.csv")
base <- file.path(base_path, "data/05_Finetuning/base_schizo_1000_vA_e118a595912c4835ae0a7bb923fb17da/quants.csv")
finetuned_epoch8 <- file.path(base_path, "data/05_Finetuning/finetuned_run_schizo_epoch8_57dc64fcac7c4882987ebf52a7c3b072/quants.csv")
finetuned_epoch12 <- file.path(base_path, "data/05_Finetuning/finetuned_run_schizo_epoch12_4fbb940fb6ad413fab636cb053f4ad7c/quants.csv")
ft <- read.csv(finetuned)
base <- read.csv(base)
ft2 <- read.csv(finetuned_epoch8)
ft12 <- read.csv(finetuned_epoch12)

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
all$llm <- all$group
all$group <- "SCZ"
set.seed(123)

real_inc <- gbd_data_global %>%
  filter(group == "SCZ",
         measure_name=="Incidence", 
         metric_name == "Number") %>%
  group_by(cause_name, age_name) %>%
  mutate(num_both_sexes = sum(val)) %>% # to add up both sex values
  filter(sex_name == "Female") %>% # to keep each age category only once
  ungroup() %>% 
  group_by(cause_name) %>%
  mutate(perc =num_both_sexes / sum(num_both_sexes))  %>%  # percentage an age category represents of all cases
  arrange(age_name)

# get
real_dist <- real_inc %>% ungroup()%>%
  select(age_name, perc) %>% arrange(age_name)
real_dist <- setNames(real_dist$perc, real_dist$age_name)

llm_list <- c("Base Model (LLM 1)", "Finetuned (Ep 3)",  "Finetuned (Ep 8)",  "Finetuned (Ep 12)" )
llm_name <- llm_list[[4]]
ad_results <- lapply(llm_list, function(llm_name) {
  print(llm_name)
  llm <- all %>%
    filter(group == "SCZ", 
           llm == llm_name
    ) %>%arrange(age_of_onset)
  # assign values to bins, equivalent to GBD data
  
  llm$age_group <- cut(llm$age_of_onset, breaks = c(seq(0, 100, 5)), labels = age_groups)
  llm$age_group_numeric <- as.numeric(llm$age_group) * 5 -2.5
  
  make_sample <- function(pmf, x_vals, n = 800) {
    sample(x_vals, size = n, replace = TRUE, prob = pmf)
  }
  ages_real <- make_sample(real_dist, x_vals = seq(2.5, 97.5, by = 5))

  ks_result <- ks.test(ages_real, llm$age_group_numeric)

  df <- data.frame(disorder = "SCZ",
                   llm = llm_name,
                   ks_test_stat_D = ks_result$statistic[[1]],
                   ks_test_p_value = ks_result$p.value[[1]]

  )
  return(df)
  
})  

ad_results <- do.call("rbind", ad_results)


ad_results$ks_test_p_value <- format_pvals(ad_results$ks_test_p_value)

write.csv(ad_results, file.path(saving_tables,"eTable15_Finetuning_Distributions_KS.csv"))



# compare finetuning sex distributions

prev <- gbd_prev_global %>%
  filter(group == "SCZ",
         measure_name=="Prevalence", 
         metric_name == "Number")  %>%
  mutate(num_both_sexes = sum(val), 
         perc_sex = val / num_both_sexes
  )


llm_list <- c("Base Model (LLM 1)", "Finetuned (Ep 3)",  "Finetuned (Ep 8)",  "Finetuned (Ep 12)" )
chi_results <- lapply(llm_list, function(llm_name) {
  print(llm_name)
  llm <- all %>%
    filter(group == "SCZ", 
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
  df <- data.frame(disorder = "SCZ",
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


all_chisqs <- chi_results
all_chisqs$gbd_perc_female <- as.character(round(all_chisqs$gbd_perc_female, 4)*100)
all_chisqs$llm_perc_female <- as.character(round(all_chisqs$llm_perc_female, 4)*100)
all_chisqs$X_squared <- as.character(round(all_chisqs$X_squared, 2))
all_chisqs$p_value <- p.adjust(all_chisqs$p_value, method = "BH")
all_chisqs <- rename(all_chisqs, p_value_adj = p_value)

all_chisqs$p_value_adj <- format_pvals(all_chisqs$p_value_adj)
write.csv(all_chisqs, file.path(saving_tables, "eTable16_Sex_Distribution_Comparison-X-squared.csv"))





