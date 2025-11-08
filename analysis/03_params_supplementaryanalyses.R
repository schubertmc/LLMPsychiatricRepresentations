library(ggplot2)
#library(strex)
#library(dplyr)

source("../MAIN/code/analysis/constants_functions.R")


path <- file.path(base_path, "/data/01_Parameters/")
files <- list.files(path, pattern = "TEMP_TOPP_CHARACTERANALYSIS.csv", recursive = T, full.names= T)
data <- lapply(files, read.csv)
data <- do.call("rbind", data)
data$patient_case <- NULL
data$llm <- str_before_first(data$folder_id, "_")
data$llm[data$llm=="openai"] <- "LLM 1"
data$llm[data$llm=="anthropic"] <- "LLM 2"
data$llm[data$llm=="llama"] <- "LLM 3"

data$temp <- str_first_number_after_first(data$file_id, "temp", decimals = T)
data$topp <- str_first_number_after_first(data$file_id, "topp", decimals = T)
data$id <- paste(data$llm, data$temp, data$topp, sep = "_")
data$age_of_onset[data$age_of_onset >150] <- -1
data$age_of_onset[data$age_of_onset <0] <- -1



suma <- data %>% 
  group_by(llm, temp, topp) %>%
  mutate(n = n(),
         non_ascii_free = sum(n_total != 0)==0)

data <- data %>% 
  group_by(llm, temp, topp) %>%
  mutate(n = n(),
  non_ascii_free = sum(n_total != 0)==0)

theme_custom <- theme_bw() + 
  theme(strip.background = element_rect(fill = "white"))

suma$non_ascii_free[suma$non_ascii_free==T] <- "Yes"
suma$non_ascii_free[suma$non_ascii_free=="FALSE"] <- "No"
data$non_ascii_free[data$non_ascii_free==T] <- "Yes"
data$non_ascii_free[data$non_ascii_free=="FALSE"] <- "No"



p1 <- ggplot(suma, aes(x = temp, topp, color = non_ascii_free)) + 
  geom_point(size=3) + 
  facet_wrap(~llm, scales="free") + 
  scale_color_manual(values = c("#8a2724", "#83b454"), name= "Non-ASCII Free")+
  theme_custom + 
  scale_y_reverse()+
theme(text =element_text(size=6))
#ggsave(paste0(path, "error_free_1.png"), width = 6, height = 2.5)

library(ggh4x)
p2 <- ggplot(data, aes(x = age_of_onset, fill = non_ascii_free)) + 
  geom_histogram() + 
  scale_fill_manual(values = c("#8a2724", "#83b454"), name = "Non-ASCII Free")+
  facet_nested(temp~llm+topp, labeller=label_both) + 
  theme_custom + 
  theme(text =element_text(size=6)) +
  xlab("Age of Onset")

p1 / p2    + plot_layout(heights = c(1,3))
ggsave(file.path(saving_folder, "eFig1_TempTopp_Params.png"), width = 8, height = 7)




########## Different prompts ##########
path <- file.path(base_path, "data/02_Prompts/different_prompts.csv")
prompts <- read.csv(path)
prompts$prompt_long <- str_before_first(prompts$filename, "_")
prompts$modelmode[prompts$modelmode=="openai"] <- "LLM 1"
prompts$modelmode[prompts$modelmode=="anthropic"] <- "LLM 2"
prompts$modelmode[prompts$modelmode=="llama"] <- "LLM 3"

table(prompts$prompt_long, prompts$modelmode)

table(prompts$prompt_long, prompts$modelmode)
table(prompts$prompt_long>250)
prompts %>% group_by(prompt_long) %>% summarize(n=n()) %>% arrange(n)
prompts$age_of_onset <- as.numeric(prompts$age_of_onset)
prompt_order <- prompts %>%
  filter(n() > 239) %>%
  distinct(prompt_long) %>%
  pull(prompt_long) 
prompt_order <- c(
  "Please create a short patient report for a patient with schizophrenia.",
  setdiff(prompt_order, "Please create a short patient report for a patient with schizophrenia.")
)


# Apply factor level ordering in both data sets
prompts <- prompts %>%
  mutate(prompt_long = factor(prompt_long, levels = prompt_order))
unique(prompts$prompt_long)

p_prompt1 <- ggplot(prompts %>% group_by(prompt_long) %>%
                      filter(n()>239)
                    , aes(x = age_of_onset)) + 
  geom_histogram(fill=blues[1]) + 
  theme_bw()+
  facet_grid(prompt_long~modelmode ) + 
  theme(strip.text.y = element_text(angle = 0, hjust = 0),
        strip.background.y = element_blank(),
        strip.background.x = element_rect(fill="white", color="white"), 
        strip.text.x = element_text(face="bold"), 
        text = element_text(size = 6)
  ) + 
  xlim(0,80)+
  xlab("Age of Onset")

sds <- prompts %>% group_by(prompt_long) %>%
  filter(n()>239) %>%
  group_by(prompt_long, modelmode) %>% summarize(n=n(), sd = sd(age_of_onset))
sds <- sds %>%
  mutate(prompt_long = factor(prompt_long, levels = rev(prompt_order)))

p_prompt2 <- ggplot(sds, aes(y =(prompt_long), x = sd, color=modelmode))+
  geom_point() + 
  theme_bw() + 
  scale_color_manual(values=blues, name = "")   +
  theme(axis.text.y = element_blank(),
        text = element_text(size = 6)
  ) +
  ylab("")

p_prompt1 + p_prompt2 + plot_layout(widths = c(6, 2))

ggsave(file.path(saving_folder, "eFig2_different_prompts.png"), width = 7, height = 5, units = "in")

prompts_mean_dif <- prompts %>% 
  group_by(prompt_long, modelmode) %>% 
  summarize(mean = mean(age_of_onset, na.rm=T), 
            max = max(age_of_onset, na.rm=T), 
            min = min(age_of_onset, na.rm=T))

prompts_mean_dif %>% 
  group_by(modelmode) %>% 
  summarize(mean_min = min(mean), 
            mean_max =max(mean)
            ) %>% 
  write.csv(file.path(saving_tables, "OTHER_differentprompts_max_min_ofthemeans.csv"))
     

prompts_mean_dif %>%
  group_by(modelmode) %>%
  summarise(
    overall_mean = mean(mean),
    se           = sd(mean) / sqrt(n()),   # n() == 20
    df           = n() - 1,
    t_crit       = qt(0.975, df),              # two-sided 95 %
    ci_lower     = overall_mean - t_crit * se,
    ci_upper     = overall_mean + t_crit * se
  ) %>%
  write.csv(file.path(saving_tables, "OTHER_differentprompts_max_min_ofthemeans_CI-.csv"))



llms <- c("LLM 1", "LLM 2", "LLM 3")      
all_tables <- list()
for (cur_model in llms) {
  print(cur_model)
  llm1_data <- prompts %>% filter(modelmode == cur_model, !is.na(age_of_onset))
  ks_results_llm1 <- lapply(prompt_order[-1], function(cur_prompt) {
    x <- llm1_data$age_of_onset[llm1_data$prompt_long == prompt_order[1]]
    y <- llm1_data$age_of_onset[llm1_data$prompt_long == cur_prompt]
    x <- cut(x, breaks = c(seq(0, 100, 5)), labels = age_groups)
    x_counts_obs <-  table(x)
    y <- cut(y, breaks = c(seq(0, 100, 5)), labels = age_groups)
    y_counts_obs <-  table(y)
    
    
    bin_centres <- seq(2.5, 97.5, by = 5)
    ages_x <- rep(bin_centres, times = as.integer(x_counts_obs))
    ages_y <- rep(bin_centres, times = as.integer(y_counts_obs))
    
    #ks_result <- ks.test(ages_x, ages_y)
    ks <- ks.test(ages_x, ages_y)
    tibble(
      model = cur_model,
      prompt1 = prompt_order[1],
      prompt2 = cur_prompt,
      p_value = ks$p.value,
      statistic = ks$statistic
    )  
  })
  ks_results_llm1 <- do.call("rbind",ks_results_llm1 )
  ks_results_llm1$LLM <- cur_model
  all_tables[[length(all_tables)+1]] <- ks_results_llm1
}
all_tables <- do.call("rbind", all_tables)
all_tables$p_adj <- p.adjust(all_tables$p_value, "BH")
all_tables$p_adj <- format_pvals(all_tables$p_adj)
all_tables$prompt1 <- NULL
all_tables$p_value <- NULL
all_tables$LLM <- NULL
all_tables %>%
  write.csv(file.path(saving_tables, paste0("eTable7_DifferentPrompts_KS_Comparison.csv")))




########## Different models ##########
browns <- c("#ffffff", "#b3ab99", "#d9d4c6")
blues <- c("#395661", "#8ea9b7", "#c1d0d9", "#ebf1f3")



path <- file.path(base_path, "data/03_DifferentModels/different_models.csv")
dif_models <- read.csv(path)
dif_models$llm <- str_before_first(dif_models$model,"_SCZ" )
dif_models$llm_group[str_starts(dif_models$llm, "claude")] <- "anthropic"
dif_models$llm_group[str_starts(dif_models$llm, "gpt")] <- "openai"
dif_models$llm_group[str_starts(dif_models$llm, "o1")] <- "openai"
dif_models$llm_group[str_starts(dif_models$llm, "Meta")] <- "llama"
dif_models$llm_group <- factor(dif_models$llm_group, levels = c("openai", "anthropic", "llama" ))
dif_models$llm <- factor(dif_models$llm, levels = c("gpt-3.5-turbo", "gpt-4o-mini", "o1-mini", "gpt-4o", "o1-preview",
                                                    "Meta-Llama-3.1-8B-Instruct-Turbo", "Meta-Llama-3.1-70B-Instruct-Turbo","Meta-Llama-3.1-405B-Instruct-Turbo",
                                                    "claude-3-haiku-20240307", "claude-3-sonnet-20240229"
                                                    
                                                    
                                                    
                                                    
                                                    ))
table(dif_models$llm)
table(dif_models$llm_group)

p_dif1 <- ggplot(dif_models, aes(x = age_of_onset)) +
  geom_histogram(fill = blues[1], bins = 50) +
  facet_wrap(llm_group~llm, nrow = 5, dir = "v") +
  theme_bw() +
  theme(strip.background = element_rect(fill = "white")) +
  xlim(0, 100) +
  xlab("Age of Onset")+ 
  theme(element_text(size = 6))




# standard deviation 
sds <- dif_models %>%
  group_by(llm, llm_group) %>%
  summarize(sd = sd(age_of_onset))


p_dif2 <- ggplot(sds, aes(y = llm, x = sd, split = llm_group)) + 
  geom_point(color=blues[1]) + 
  facet_wrap(~llm_group, ncol=2, scale="free_y", )+
  theme_bw() + theme(strip.background = element_rect(fill="white")) +
  ylab("") + 
  theme(element_text(size = 6))
p_dif1 / (p_dif2) + plot_layout(heights = c(3,1))
ggsave(file.path(saving_folder, "eFig3_different_models.png"), width = 7, height = 8, units = "in")


dif_models %>% 
  group_by(llm_group, llm) %>%
  summarize(mean = mean(age_of_onset)) %>%
  group_by(llm_group) %>%
  summarize(mean_min = min(mean), 
            mean_max =max(mean)
  ) %>% 
  write.csv(file.path(saving_tables, "OTHER_differentmodels_max_min_ofthemeans.csv"))




