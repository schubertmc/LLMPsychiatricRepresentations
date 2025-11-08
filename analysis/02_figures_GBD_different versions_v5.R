# Packages, variables, etc

source("../MAIN/code/analysis/constants_functions.R")

data <- read.csv(file.path(processed_folder, "main_dataset_v1.csv"))
long <- read.csv(file.path(processed_folder, "long_dataset_v1.csv"))
real_inc <- read.csv(file.path(processed_folder, "GBD_real_inc_v1.csv"))
real_inc_usa <- read.csv(file.path(processed_folder, "USA_GBD_real_inc_v1.csv"))
gbd <-  read.csv(file.path(processed_folder, "GBD_real_prev_v1.csv"))
gbd_usa <- read.csv(file.path(processed_folder, "USA_GBD_real_prev_v1.csv")) 

data$llm <- factor(data$llm, levels = c("LLM 1", "LLM 2", "LLM 3"))
data$group <- factor(data$group, mental_disorders_short)

real_inc$age_name_short <- factor(real_inc$age_name_short, levels = age_groups_short)
real_inc$group <- factor(real_inc$group, mental_disorders_short)
real_inc_usa$age_name_short <- factor(real_inc_usa$age_name_short, levels = age_groups_short)
real_inc_usa$group <- factor(real_inc_usa$group, mental_disorders_short)

gbd$sex_name <- factor(gbd$sex, levels = c("Female", "Male"))
gbd$group <- factor(gbd$group, mental_disorders_short)

gbd_usa$sex_name <- factor(gbd_usa$sex, levels = c("Female", "Male"))
gbd_usa$group <- factor(gbd_usa$group, mental_disorders_short)


long$group <- factor(long$group, mental_disorders_short)


### Functions ###############
# Function to generate Table for MS
createMainTable <- function(data, model) {
  filt <- data %>% 
    filter(llm == model)
  
  suma <- filt %>%
    group_by(group) %>%
    summarize(
      n = n(),
      age_of_onset_mean = mean(age_of_onset, na.rm = T),
      age_of_onset_sd = sd(age_of_onset, na.rm = T),
      age_current_mean = mean(age_current, na.rm = T),
      age_current_sd = sd(age_current, na.rm = T),
      .groups = "drop"
    ) %>%
    mutate(
      N = as.character(n),
      AGE_OF_ONSET = paste0(round(age_of_onset_mean,1), " (",round(age_of_onset_sd,1),")" ),
      AGE_CURRENT = paste0(round(age_current_mean,1), " (",round(age_current_sd,1),")" ),
    ) %>%
    select(-c(n, 
              age_of_onset_mean,
              age_of_onset_sd, 
              age_current_mean, 
              age_current_sd)) %>%
    ungroup()
  suma$Age <- rep("", nrow(suma))
  suma <- suma %>% 
    relocate(Age, .after = N)
  colnames(suma) <- c("group", "N","Age, mean (SD), y", 
                      "Age of Onset",
                      "Current Age")
  
  # Define categorical variables manually or detect them dynamically
  vars <- variables_keys
  var <- "smoking"
  table_parts <- list()
  for (var in vars) {
    print(var)
    
    cur_factors <- c(levels(secondary_factors[[variable_mapping[[var]]]]), NA)
    filt[,var] <- factor(filt[,var], levels = cur_factors)
    cur_part <- filt %>%
        group_by(group) %>%
        mutate(n_pergroup = n()) %>%  # Compute group size
        group_by(group, !!sym(var)) 
    
    cur_part <- cur_part %>%
      group_by(group, !!sym(var)) %>%
      summarize(
        n_count = n(),
        n_pergroup = first(n_pergroup),
        .groups = "drop"
      ) %>%
      complete(
        group = unique(filt$group),
        !!sym(var) := cur_factors,
        fill = list(n_count = 0)# n_pergroup = 1)  # Prevent division by 0
      ) %>%
      mutate(
        perc = n_count / n_pergroup,
        n_formatted = paste0(n_count, " (", round(perc * 100, 1), ")")
      ) %>%
      select(group, !!sym(var), n_formatted) %>%
      pivot_wider(
        names_from = all_of(var),
        values_from = n_formatted,
        names_prefix = paste0(var, "_n_")
      )

    
    #%>%  
      # summarize(
      #   n_count = n(),
      #   perc = n_count / first(n_pergroup),  # Ensure n_pergroup is preserved
      #   .groups = "drop"
      # ) %>%
      # mutate(n_formatted = paste0(n_count, " (", round(perc * 100, 1), ")")) %>%  # Format count + percent
      # select(-c(n_count, perc)) %>%
      # pivot_wider(
      #   names_from = all_of(var),
      #   values_from = n_formatted,
      #   names_prefix = paste0(var, "_n_")  # Use correct prefix
      # )
    cur_part
    columns <- str_after_first(colnames(cur_part), "_n_")
    cur_factors[is.na(cur_factors)] <- "NA"
    match_order <- match(cur_factors, columns) 
    match_order <- match_order[!is.na(match_order)]
    cur_part <- cur_part %>%
      select(group, any_of(match_order))
    spaceholder <- data.frame("")
    colnames(spaceholder) <- paste0(variable_mapping[[var]], ", No. (%)")
    table_parts[[length(table_parts)+1]] <- spaceholder
    table_parts[[length(table_parts)+1]] <- cur_part
    
  }
  
  all_bound <- cbind(suma, table_parts)
  all_bound <- all_bound[,!duplicated(colnames(all_bound))]
  
  long_table <- all_bound %>%
    pivot_longer(cols = -group)
  
  final_table <- long_table %>%
    pivot_wider(names_from = group,
                values_from = value)
  # replace NA with 0, 
  final_table[,] <- lapply(final_table, function(x) replace(x, is.na(x), "0 (0)"))
  final_table[,] <- lapply(final_table, function(x) replace(x, x == "0 (NA)", "0 (0)"))
  
  
  final_table <- final_table %>%
    select(name, all_of(mental_disorders_short))
  
  final_table$name[str_detect(final_table$name, "_n_")] <- str_after_first(final_table$name[str_detect(final_table$name, "_n_")], "_n_")
  
  write.csv(final_table,file.path(saving_tables, paste0(model, "_MainTable.csv"))) 

}

############  Functions######



#model <- "LLM 1"

# Main Tables
createMainTable(data, model = "LLM 1")
createMainTable(data, model = "LLM 2")
createMainTable(data, model = "LLM 3")


# Figure 1: Graphical abstract
# 

### Figure 2: #####
# Age of Onset

data$llm <- factor(data$llm, levels = c("LLM 1", "LLM 2", "LLM 3"))

table(is.na(data$age_of_onset)) %>% 
  write.csv(file.path(saving_tables, "OTHER_age_of_onset_n_numbers.csv" ))


llm_onset_plot <- ggplot(data 
                         , aes(x = age_of_onset, fill = llm)) + 
  geom_histogram(aes(y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]),
                 bins = 100, color = "grey40", size = 0.2) + 
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



p_real <- ggplot(real_inc,aes(x =age_name_short, y =perc )) + 
  theme_bw()+
  geom_bar(stat = "identity", fill = browns[3],color = "grey40",size=0.2 ) + 
  xlab("Incidence") + 
  ylab("[%]")+
  #  theme(axis.text.x= element_blank())+
  facet_grid(gbd~group, scales="free", switch="y")  + 
  theme(title= element_text(size = 7, face = "plain"),
        text = element_text(size = 7),
        strip.text.x =element_blank(),# element_text(face = "bold", size = 9),
        axis.text.x = element_text(size = 7),
        axis.text.y = element_text(size = 7),
        legend.position = "none"
  ) +
  scale_x_discrete(
    breaks = c("25-29 y", "50-54 y", "75-79 y", "100+ y"), # Choose categories to show
    labels = c("25", "50", "75", "100") # Set numeric-like labels
  )+
  theme(strip.background = element_blank(), 
        strip.text.y =  element_text(face="bold", hjust=0, size=7)) 




age_plot <- llm_onset_plot / p_real + 
  plot_layout(heights = c(3,1)) 
p_real
age_plot

# Sex Analyses 
data$llm <- factor(data$llm, levels = c("LLM 3", "LLM 2", "LLM 1"))


llm_sex <- ggplot(data %>%
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




# GBD Sex
gbd_sex <- ggplot(gbd %>%
                    filter(cause_name %in% mental_disorders)
                  , aes(x=val,y=llm ,fill=sex_name)) + 
  geom_bar( stat="identity", position ="fill") + 
  facet_wrap(~group, ncol =8)+
  
  
  scale_fill_manual(values = bluebrowns[c(5,3)], name = "Sex")+
  theme_bw()+
  theme(strip.background = element_blank(), 
        strip.text = element_text(face="plain", hjust=0),
        strip.text.x = element_blank(),
        title = element_text(size = 8),
        legend.position ="none",
        axis.text.x = element_text(size = 7),
        axis.text.y = element_text(size = 7, face="bold"),
  ) + 
  ylab("") +xlab("[%]") +
  scale_x_continuous(labels = function(x) x *100)



sex_plot <- llm_sex + gbd_sex + plot_layout(heights = c(3,1))
sex_plot

stretch <-4
# Arrange plots with correct layout
llm_onset_plot / p_real / llm_sex / gbd_sex + 
  plot_layout(heights = c(stretch*3, stretch*1, 3, 1), tag_level = 'new')+
  plot_annotation(tag_levels = list(c('A', ' ', "B", " "))) & theme(plot.tag = element_text(face = 'bold'))

ggsave(file.path(saving_folder, "Fig2_Age_and_Sex.png"), width = 11, height = 8.5, units = "in")


#### Supplementary Figure GBD Data

p_real_global_ui <- ggplot(real_inc,aes(x =age_name_short, y =num_both_sexes )) + 
  theme_bw()+
  geom_bar(stat = "identity", fill = browns[3],color = "grey40",size=0.2 ) + 
  geom_errorbar(aes(ymin=num_both_sexes_lower, ymax=num_both_sexes_upper), 
                color="grey60"
  )+ 
  xlab("Incidence") + 
  ylab("N")+
  #  theme(axis.text.x= element_blank())+
  facet_wrap(~group, scales="free", nrow=2)+
  #facet_grid(gbd~group, scales="free", switch="y")  + 
  scale_x_discrete(
    breaks = c("25-29 y", "50-54 y", "75-79 y", "100+ y"), # Choose categories to show
    labels = c("25", "50", "75", "100") # Set numeric-like labels
  )+
  theme(
    text           = element_text(size = 7),
    plot.title     = element_text(size = 8, face = "bold"),
    strip.background = element_blank(),
    strip.text.x   = element_text(face = "bold", size = 7, hjust = 0),
    strip.text.y   = element_text(face = "bold", size = 7, hjust = 0),
    axis.text.x    = element_text(size = 7),
    axis.text.y    = element_text(size = 7),
    legend.position = "none"
  )+
  ggtitle("Global")


p_real_usa_ui <- ggplot(real_inc_usa,aes(x =age_name_short, y =num_both_sexes )) + 
  theme_bw()+
  geom_bar(stat = "identity", fill = browns[3],color = "grey40",size=0.2 ) + 
  geom_errorbar(aes(ymin=num_both_sexes_lower, ymax=num_both_sexes_upper), 
                color="grey60"
  )+ 
  xlab("Incidence") + 
  ylab("N")+
  #  theme(axis.text.x= element_blank())+
  facet_wrap(~group, scales="free", nrow=2)+
  #facet_grid(gbd~group, scales="free", switch="y")  + 
  
  scale_x_discrete(
    breaks = c("25-29 y", "50-54 y", "75-79 y", "100+ y"), # Choose categories to show
    labels = c("25", "50", "75", "100") # Set numeric-like labels
  )+
  theme(
    text           = element_text(size = 7),
    plot.title     = element_text(size = 8, face = "bold"),
    strip.background = element_blank(),
    strip.text.x   = element_text(face = "bold", size = 7, hjust = 0),
    strip.text.y   = element_text(face = "bold", size = 7, hjust = 0),
    axis.text.x    = element_text(size = 7),
    axis.text.y    = element_text(size = 7),
    legend.position = "none"
  )+
  ggtitle("USA")


#sex
pd <- position_dodge(width = 0.9)
sex_global_ui <- ggplot(gbd %>%
         filter(cause_name %in% mental_disorders)
       , aes(y=val,x=llm ,fill=sex_name)) + 
  geom_bar( stat="identity", position = pd) + 
  geom_errorbar(aes(ymin=lower, ymax=upper, width=0.5), 
                position= pd,
                color="grey60")+
  facet_wrap(~group, ncol =8, scales = "free")+
    scale_fill_manual(values = bluebrowns[c(5,3)], name = "Sex")+
  theme_bw()+
  
  theme(
    text           = element_text(size = 7),
    plot.title     = element_text(size = 8, face = "bold"),
    strip.background = element_blank(),
    strip.text.x   = element_text(face = "bold", size = 7, hjust = 0),
    strip.text.y   = element_text(face = "bold", size = 7, hjust = 0),
    axis.text.x    = element_text(size = 7),
    axis.text.y    = element_text(size = 7)
  )+  ylab("N")  + 
  ggtitle("Global")+ 
  xlab("")



sex_usa_ui <- ggplot(gbd_usa %>%
                          filter(cause_name %in% mental_disorders)
                        , aes(y=val,x=llm ,fill=sex_name)) + 
  geom_bar( stat="identity", position = pd) + 
  geom_errorbar(aes(ymin=lower, ymax=upper, width=0.5), 
                position= pd,
                color="grey60")+
  facet_wrap(~group, ncol =8, scales = "free")+
  scale_fill_manual(values = bluebrowns[c(5,3)], name = "Sex")+
  theme_bw()+
  theme(
    text           = element_text(size = 7),
    plot.title     = element_text(size = 8, face = "bold"),
    strip.background = element_blank(),
    strip.text.x   = element_text(face = "bold", size = 7, hjust = 0),
    strip.text.y   = element_text(face = "bold", size = 7, hjust = 0),
    axis.text.x    = element_text(size = 7),
    axis.text.y    = element_text(size = 7),
    legend.position = "none"
  )+  ylab("N")  + 
  ggtitle("USA") + 
  xlab("")



p_efig <- p_real_global_ui / p_real_usa_ui / sex_global_ui/ sex_usa_ui + plot_layout(heights = c(3,3,1,1))
p_efig
#
ggsave(plot = p_efig, file.path(saving_folder, "eFig4_Global_and_USA_Distribution_Differences_UI.png"), width = 8.5, height = 8.5, units = "in")





#### Figure 3: Secondary Outcomes
plots <- list()
for (cur_variable in variables) {
  df <- long %>% 
    filter(name_long == cur_variable)
  df$value <- factor(df$value, levels = levels(secondary_factors[[cur_variable]]))
  p1 <- ggplot(df, aes(y = group, fill = value)) + 
    theme_bw()+
    ylab("")+
    xlab("[%]")+
    theme(legend.position = "right", 
          strip.background = element_blank(), 
          strip.text = element_text(face="plain", hjust=0, size=6),
          title = element_text(size = 8),
          axis.text.x = element_text(size = 6),
          axis.text.y = element_text(size = 6), 
          legend.margin= margin(0, 0, 0, 0, unit='pt'),
          legend.box.margin = margin(0, 0, 0, 0, unit='pt'),
          legend.key.size = unit(5, "points"),
          legend.text = element_text(size = 7)
    ) + 
    geom_bar(position="fill") + 
    scale_fill_manual(values = c(bluebrowns2, colorset), name = "")+
    facet_grid(~llm, switch="y")  + 
    ggtitle(cur_variable)+
    scale_x_continuous(labels = function(x) x *100)
  plots[[length(plots)+1]] <- p1
}
#if legend right

Reduce(`+`, plots) + plot_layout(ncol = 2)

ggsave(file.path(saving_folder, "Fig3_Secondary_Outcomes.pdf"), width = 9, height = 6)
ggsave(file.path(saving_folder, "Fig3_Secondary_Outcomes.png"), width = 9, height = 6)

data$BMI <- as.numeric(data$BMI)
max(data$BMI, na.rm=T)


bmi_table <- data %>% 
group_by(group, llm) %>% 
  summarize(mean = mean(BMI, na.rm = T), 
            sd = sd(BMI, na.rm = T))
bmi_table$mean <- format(bmi_table$mean,digits=4)
bmi_table$sd <- format(bmi_table$sd,digits=4)
write.csv(bmi_table, file.path(saving_tables, "eTable10_BMI.csv"))


## Figure 4 
phq9_mat <- read.csv(file.path(processed_folder, "phq_9_mat_v1.csv"), row.names = "X")


# Define a named vector of colors for the LLM levels
llm_colors <- c(
  "LLM 1" = blues[1],
  "LLM 2" = blues[2],
  "LLM 3" = blues[3]
)


target_rids <- rownames(phq9_mat)
llm_anno <- data$llm[match(target_rids, data$rid)]


# Add colors to the HeatmapAnnotation
column_anno <- HeatmapAnnotation(
  LLM = llm_anno,
  col = list(LLM = llm_colors)
)


#column_anno <- HeatmapAnnotation(LLM = data$llm[target_bool])
#pdf("../../plots/Fig4_heatmap_phq9_clustering.pdf", width = 7, height = 2.5)
pdf(file.path(saving_folder, paste("Fig4_heatmap_phq9_clustering.pdf")), width = 7, height = 2.5)

colnames(phq9_mat) <- paste(colnames(phq9_mat), c("Little interest", 
                                                  "Feeling down, depressed", 
                                                  "Trouble sleeping", 
                                                  "Feeling tired/low energy", 
                                                  "Eating over/under", 
                                                  "Feeling like a failure", 
                                                  "Trouble concentrating", 
                                                  "Psychomotor agitation/retardation", 
                                                  "Suicide ideation"), sep = " ")
p1 <- Heatmap(t(phq9_mat), 
      #rect_gp = gpar(col ="white" , lwd = 2),
        cluster_rows=T, 
        cluster_columns = T, 
        show_row_names = T, 
        show_column_names = F,
        name = "PHQ-9", 
        top_annotation = column_anno, 
        col= c("yellow", "red"), 
      use_raster=T, raster_quality = 5
        #row_split = 5
        )
draw(p1)
dev.off()

dim(phq9_mat) %>%write.csv(file.path(saving_tables, "OTHER_PQH9_summary_stats_N_counts.csv" ))


panss_mat <- read.csv(file.path(processed_folder, "panss_mat_v1.csv"), row.names = "X")
target_rids <- rownames(panss_mat)
llm_anno <- data$llm[match(target_rids, data$rid)]

# Add colors to the HeatmapAnnotation
column_anno <- HeatmapAnnotation(
  LLM = llm_anno,
  col = list(LLM = llm_colors)
)


pdf(file.path(saving_folder, paste("eFig7_heatmap_panss_clustering-3.pdf")), width = 7, height = 4)
panss_mat_plotting <- panss_mat
colnames(panss_mat_plotting) <- str_to_title(str_replace_all(colnames(panss_mat_plotting), "_", " "))

p2 <- Heatmap(t(panss_mat_plotting), 
        cluster_rows=T, 
        cluster_columns = T, 
        show_row_names = T,
        show_column_names = F,
        row_names_gp = gpar(fontsize=6),
        name = "PANSS",
        top_annotation = column_anno,
        use_raster=T, raster_quality = 5,
        #right_annotation = row_anno, 
        col= c("yellow",  "red")
        #row_split = 5
)
draw(p2)
dev.off()


dim(panss_mat) %>%write.csv(file.path(saving_tables, "OTHER_PANSS_summary_stats_N_counts.csv" ))


# PHQ-9 and PANSS tables
phq9_mat <- read.csv(file.path(processed_folder, "phq_9_mat_v1.csv"), row.names = "X")

phq9_mat$q_sum <- rowSums(phq9_mat[,phq9_vector])
phq9_mat$llm <- str_before_first(rownames(phq9_mat), "_")
phq9_mat$llm[phq9_mat$llm=="openai"] <- "LLM 1"
phq9_mat$llm[phq9_mat$llm=="anthropic"] <- "LLM 2"
phq9_mat$llm[phq9_mat$llm=="llama"] <- "LLM 3"
ggplot(phq9_mat, aes(x = llm, y = q_sum)) + 
  geom_boxplot()


phq9_mat %>%
  group_by(llm) %>%
  dplyr::summarize(mean = mean(q_sum), 
                   sd = sd(q_sum), 
                   max = max(q_sum), 
                   min = min(q_sum)
                   ) %>%
  write.csv(file.path(saving_tables, "OTHER_PQH9_summary_stats.csv" ))




values_by_question_table <- phq9_mat %>%
  pivot_longer(all_of(phq9_vector),names_to = "question") %>%
  group_by(question, llm) %>%
  dplyr::summarize(
                   mean = mean(value), 
                   sd = sd(value), 
                   max = max(value), 
                   min = min(value)
  ) 

ext <- data.frame(question = paste0("q", 1:9),
description = c("Little interest", 
                "Feeling down, depressed", 
                "Trouble sleeping", 
                "Feeling tired/low energy", 
                "Eating over/under", 
                "Feeling like a failure", 
                "Trouble concentrating", 
                "Psychomotor agitation/retardation", 
                "Suicide ideation"))
values_by_question_table <- merge(values_by_question_table, ext, by = "question") 
values_by_question_table <- values_by_question_table%>% relocate(question, description)
values_by_question_table$mean <- format(values_by_question_table$mean, digits=2)
values_by_question_table$sd <- format(values_by_question_table$sd, digits=2)
write.csv(values_by_question_table, file.path(saving_tables, "eTable11_PHQ9_QuestionValues.csv" ))


q_analysis <- colMeans(phq9_mat[,phq9_vector])
q_analysis[order(q_analysis)] %>%  write.csv(file.path(saving_tables, "OTHER_phq9_summary_stats_question_means.csv" ))


#
panss_mat <- read.csv(file.path(processed_folder, "panss_mat_v1.csv"), row.names = "X")

panss_mat$panss_sum <- rowSums(panss_mat[,panss_vector])
panss_mat$llm <- str_before_first(rownames(panss_mat), "_")
panss_mat$llm[panss_mat$llm=="openai"] <- "LLM 1"
panss_mat$llm[panss_mat$llm=="anthropic"] <- "LLM 2"
panss_mat$llm[panss_mat$llm=="llama"] <- "LLM 3"
ggplot(panss_mat, aes(x = llm, y = panss_sum)) + 
  geom_boxplot()
panss_mat %>%
  group_by(llm) %>%
  dplyr::summarize(mean = mean(panss_sum), 
                   sd = sd(panss_sum), 
                   max = max(panss_sum), 
                   min = min(panss_sum)
  ) %>%
  write.csv(file.path(saving_tables, "OTHER_panss_summary_stats.csv" ))

panss_item_analysis <- colMeans(panss_mat[,panss_vector])
panss_item_analysis[order(panss_item_analysis)] %>%  write.csv(file.path(saving_tables, "OTHER_panss_summary_stats_items_means.csv" ))


panss_q_summary <- panss_mat %>% 
  pivot_longer(cols = all_of(panss_vector), names_to = "question") %>%
  group_by(question, llm) %>%
  dplyr::summarize(mean = mean(value), 
                   sd = sd(value), 
                   max = max(value), 
                   min = min(value)
) 

panss_q_summary$question <- factor(panss_q_summary$question, levels = panss_vector)
panss_q_summary <- panss_q_summary %>% 
  arrange(question)
panss_q_summary$mean <- format(panss_q_summary$mean, digits = 2)
panss_q_summary$sd <- format(panss_q_summary$sd, digits = 2)
write.csv(panss_q_summary, file.path(saving_tables, "eTable12_PANSS_QuestionValues.csv" ))

#




######## PANSS and PHQ9 - Stiller - comparison 
phq9_mat <- read.csv(file.path(processed_folder, "phq_9_mat_v1.csv"), row.names = "X")
# 
# "q1": int,  # Little interest or pleasure in doing things
# "q2": int,  # Feeling down, depressed, or hopeless
# "q3": int,  # Trouble falling or staying asleep, or sleeping too much
# "q4": int,  # Feeling tired or having little energy
# "q5": int,  # Poor appetite or overeating
# "q6": int,  # Feeling bad about yourself — or that you are a failure or have let yourself or your family down
# "q7": int,  # Trouble concentrating on things, such as reading the newspaper or watching television
# "q8": int,  # Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual
# "q9": int,  # Thoughts that you would be better off dead, or of hurting yourself in some way



#Sample 2 included 46 259 veterans with an MDD diagnosis in the EHR who also met the corresponding DSM-5 criteria as assessed with the Patient Health Questionnaire (PHQ-9). The PHQ-9 assesses 9 symptoms each rated on a 4-point Likert scale ranging from 0 (not at all) to 3 (nearly every day). 
#A score of 2 or higher defined symptom presence.

#Sample 3 was assessed using the Positive and Negative Syndrome Scale (PANSS) and rated on a 7-point scale from 1 (absent) to 7 (extreme). 
#Symptom presence was defined as scores of 2 or higher, indicating at least minimal symptom presence.22 PANSS symptoms were mapped onto DSM-5 criteria, and 3930 individuals with a probable diagnosis of schizophrenia were included.

spiller <- data.frame(
  question = paste0("q", 1:9),
  description = c("Little interest", 
               "Feeling down, depressed", 
               "Trouble sleeping", 
               "Feeling tired/low energy", 
               "Eating over/under", 
               "Feeling like a failure", 
               "Trouble concentrating", 
               "Psychomotor agitation/retardation", 
               "Suicide ideation"),
  perc = c(72.5, 72.0, 61.3, 63.1, 61.2, 63.1, 63.1, 62.6, 61.3)
)
phq9_mat$llm <- str_before_first(rownames(phq9_mat), "_")

phq9_mat_long <- phq9_mat %>% 
  pivot_longer(cols = colnames(phq9_mat)[-10], names_to = "question")
summarized <- phq9_mat_long %>% 
  group_by(llm, question) %>%
  summarize(n = n(),
            n_present = sum(value >= 2),
            n_absence = sum(value < 2),
            perc =  100*n_present / n
            )

spiller$llm <- "Spiller et al."


bound <- rbind(summarized, spiller)
bound$llm[bound$llm=="openai"] <- "LLM 1"
bound$llm[bound$llm=="anthropic"] <- "LLM 2"
bound$llm[bound$llm=="llama"] <- "LLM 3"
bound$llm <- factor(bound$llm, levels =rev(c("Spiller et al.", 
                                          "LLM 1", "LLM 2", "LLM 3")))


bound$question <- factor(bound$question,levels = rev(paste0("q", 1:9) ))


bound <- merge(bound, spiller %>% select(question, description), by = "question")
bound$q_desc <- paste(bound$question, "-", bound$description.y)
bound$q_desc <- factor(bound$q_desc, levels = rev(c(unique(bound$q_desc))))
ggplot(bound, aes(y = q_desc, perc, group=llm, fill=llm)) + 
  geom_bar(stat="identity", position="dodge", color="grey50") + 
  scale_fill_manual(values=c(blues[1:3], browns[2]), name = "") + 
  theme_bw()  + 
  ggtitle("PHQ-9") + 
  xlab("% endorsed Spiller et al. vs LLM (PHQ-9 Score >=2)") + 
  theme(axis.text.y = element_text(color="black"), 
        element_text(size = 6)
        ) + 
  theme(strip.background = element_blank(), 
        strip.text = element_text(face="plain", hjust=0),
        strip.text.x = element_blank(),
        title = element_text(size = 8))+
  ylab("") 
  

ggsave(file.path(saving_folder, "Fig4_PHQ9_Comparison.png"), width = 5, height = 4, units = "in")


symp_prev_tab <- bound %>% 
  select(llm, question, description.y, perc) %>%
  pivot_wider(names_from = llm, values_from = perc)
symp_prev_tab$LLM_mean <- apply(data.frame(symp_prev_tab$`LLM 1`, symp_prev_tab$`LLM 2`,symp_prev_tab$`LLM 3`), 1, mean)
symp_prev_tab <- relocate(symp_prev_tab,.after="description.y", c("LLM 1", "LLM 2", "LLM 3" ,"LLM_mean", "Spiller et al." ))
symp_prev_tab$`LLM 1` <- round(symp_prev_tab$`LLM 1`, 2)
symp_prev_tab$`LLM 2` <- round(symp_prev_tab$`LLM 2`, 2)
symp_prev_tab$`LLM 3` <- round(symp_prev_tab$`LLM 3`, 2)
symp_prev_tab$`LLM_mean` <- round(symp_prev_tab$`LLM_mean`, 2)

#46,259

# for each question: compare chisq test with 

llm_list <- c("LLM 1", "LLM 2", "LLM 3")
llm_name <- llm_list[[1]]
cur_question <- "q1"

unique(bound$llm)
spiller_data <- bound %>% 
  filter(question == cur_question, 
         llm == "Spiller et al.")



### func 
compareChisqPerSymptom <- function(bound, cur_question, FILT="Spiller et al." ) {
  print(cur_question)
  llm_data <- bound %>% 
    filter(question == cur_question
    )
  spiller_data <- bound %>% 
    filter(question == cur_question, 
           llm == FILT)

  llm_list <- c("LLM 1", "LLM 2", "LLM 3")
  chi_results <- lapply(llm_list, function(llm_name) {
    print(llm_name)
    llm <- llm_data %>%
             filter(llm == llm_name) 
    
    n_total <- sum(llm$n_present, llm$n_absence)

    
    cur_mat <- matrix(c(llm$n_present, llm$n_absence, 
                           (spiller_data$perc/100)*46259, 46259 - (spiller_data$perc/100)*46259 ),
                         nrow=2, byrow = T)
    print(cur_mat)
    
    
    
    cramers_v <- rcompanion::cramerV(cur_mat)[[1]]
    
    res <-chisq.test(cur_mat)
    df <- data.frame(item = cur_question,
                     llm = llm_name,
                     X_squared = res$statistic,
                     llm_perc_present = llm$n_present/n_total, 
                     spiller_perc_present = spiller_data$perc,
                     p_value = res$p.value, 
                     cramers_v = cramers_v
    )
    return(df)
    
  })
  
  
  chi_results <- do.call("rbind", chi_results)
  
  return(chi_results)
  
}
### func 


all_chisqs <- lapply(phq9_vector, bound = bound, compareChisqPerSymptom, FILT="Spiller et al.")
all_chisqs <- do.call("rbind", all_chisqs)
all_chisqs$X_squared <- as.character(round(all_chisqs$X_squared, 2))
all_chisqs$p_value <- p.adjust(all_chisqs$p_value, method = "BH")
all_chisqs <- rename(all_chisqs, p_value_adj = p_value)
all_chisqs$p_value_adj <- format_pvals(all_chisqs$p_value_adj)
chisqs_wid <- pivot_wider(all_chisqs, id_cols = item, names_from = llm, values_from = c(X_squared, p_value_adj, cramers_v), 
            names_vary = "slowest")

symp_prev_tab_comb <- merge(symp_prev_tab, chisqs_wid, by.x = "question", by.y = "item")

write.csv(symp_prev_tab_comb, file.path(saving_tables, "eTable13_SymptomPrevalencePHQ9.csv"))

# 

## ZI data
zi <- read.csv(file.path(base_path, "data/comps/zidata/panss_share.csv"))


#Replace column names of panss_mat using panss_map
zi <- zi %>% select(panss_map$zi_item)
colnames(zi) <-panss_map$panss_mat_item[match(colnames(zi), panss_map$zi_item)]
rownames(zi) <- paste0("zi_cohort_", 1:nrow(zi))


panss_mat <- read.csv(file.path(processed_folder, "panss_mat_v1.csv"), row.names = "X")
panss_bound <- rbind(panss_mat, zi)

group <- str_before_first(rownames(panss_bound), "_")
group[group=="openai"] <- "LLM 1"
group[group=="anthropic"] <- "LLM 2"
group[group=="llama"] <- "LLM 3"

cor_zi <- cor(zi)
cor_llm1 <- cor(panss_bound[group == "LLM 1",])
cor_llm2 <- cor(panss_bound[group == "LLM 2",])
cor_llm3 <- cor(panss_bound[group == "LLM 3",])

colnames(cor_zi) == colnames(cor_llm3)

dist1 <- as.dist(1 - cor_llm1%>%as.matrix())
dist2 <- as.dist(1 - cor_llm2%>%as.matrix())
dist3 <- as.dist(1 - cor_llm3%>%as.matrix())
dist_zi <- as.dist(1- cor_zi %>% as.matrix())

d1zi <- mantel(dist1, dist_zi, method = "spearman", permutations = 999)
d2zi <- mantel(dist2, dist_zi, method = "spearman", permutations = 999)
d3zi <- mantel(dist3, dist_zi, method = "spearman", permutations = 999)

data.frame(
  Comparison = c("LLM 1 vs CIMH", "LLM 2 vs CIMH", "LLM 3 vs CIMH"),
  Mantel_r = c(d1zi$statistic, d2zi$statistic, d3zi$statistic),
  P_value = c(d1zi$signif, d2zi$signif, d3zi$signif),
  Permutations = c(d1zi$permutations, d2zi$permutations, d3zi$permutations)
) %>% 
  write.csv(file.path(saving_tables, "Other_XX_MantelComps.csv"), row.names = FALSE)


#zi
zi_long <- zi %>% 
  pivot_longer(cols = colnames(zi), names_to = "item")
zi_summarized <- zi_long %>% 
  group_by(item) %>%
  summarize(n = n(),
            n_present = sum(value >= 2),
            n_absence = sum(value < 2),
            perc =  100*n_present / n
  )


panss_bound$group <- str_before_first(rownames(panss_bound), "_")
panss_bound$group[panss_bound$group=="openai"] <- "LLM 1"
panss_bound$group[panss_bound$group=="anthropic"] <- "LLM 2"
panss_bound$group[panss_bound$group=="llama"] <- "LLM 3"
colnames(panss_bound)
panss_mat_long <- panss_bound %>% 
  pivot_longer(cols = colnames(panss_bound)[-31], names_to = "item")
summarized_panss <- panss_mat_long %>% 
  group_by(group, item) %>%
  summarize(n = n(),
            n_present = sum(value >= 2),
            n_absence = sum(value < 2),
            perc =  100*n_present / n
  )

summarized_panss$subscale <- substring(summarized_panss$item, 1, 1)


summarized_panss$group[summarized_panss$group=="zi"] <- "CIMH Cohort"
# Filter data by subscale
p_data <- subset(summarized_panss, subscale == "p")
n_data <- subset(summarized_panss, subscale == "n")
g_data <- subset(summarized_panss, subscale == "g")

# Plot for P subscale
plot_p <- ggplot(p_data, aes(y = item, x = perc, fill = group)) +
  geom_bar(stat = "identity", position = "dodge") +
  scale_fill_manual(values = c(blues[1:3], browns[2]), name = "") +
  theme_bw() +
  ylab("")+  
  xlab("[%] PANSS Score >=2")+
  ggtitle("Positive Subscale") + 
  theme(text = element_text(size = 6))

# Plot for N subscale
plot_n <- ggplot(n_data, aes(y = item, x = perc, fill = group)) +
  geom_bar(stat = "identity", position = "dodge") +
  scale_fill_manual(values = c(blues[1:3], browns[2]), name = "") +
  theme_bw() +
  ylab("")+
  xlab("[%] PANSS Score >=2")+
  ggtitle("Negative Subscale")+ 
  theme(text = element_text(size = 6))

# Plot for G subscale
plot_g <- ggplot(g_data, aes(y = item, x = perc, fill = group)) +
  geom_bar(stat = "identity", position = "dodge") +
  scale_fill_manual(values = c(blues[1:3], browns[2]), name = "") +
  theme_bw() +
  ylab("")+
  xlab("[%] PANSS Score >=2")+
  ggtitle("General Psychopathology Subscale")+ 
  theme(text = element_text(size = 6))

# Combine the plots using patchwork and adjust heights
combined_plot <- plot_p / plot_n / plot_g + plot_layout(heights = c(7, 7, 16))  # Adjust heights as needed
ggsave(file.path(saving_folder, paste("eFig8_Symptom_combination_panss_comparisons.png")), width = 4, height =5, units = "in")



symp_prev_tab <- summarized_panss %>% 
  select(group, item, perc) %>%
  pivot_wider(names_from = group, values_from = perc)
symp_prev_tab$LLM_mean <- apply(data.frame(symp_prev_tab$`LLM 1`, symp_prev_tab$`LLM 2`,symp_prev_tab$`LLM 3`), 1, mean)
symp_prev_tab <- relocate(symp_prev_tab,.after="item", c("LLM 1", "LLM 2", "LLM 3" ,"LLM_mean", "CIMH Cohort"))
symp_prev_tab$`LLM 1` <- round(symp_prev_tab$`LLM 1`, 2)
symp_prev_tab$`LLM 2` <- round(symp_prev_tab$`LLM 2`, 2)
symp_prev_tab$`LLM 3` <- round(symp_prev_tab$`LLM 3`, 2)
symp_prev_tab$`LLM_mean` <- round(symp_prev_tab$`LLM_mean`, 2)
symp_prev_tab$item  <- factor(symp_prev_tab$item, levels = panss_vector)
symp_prev_tab<- symp_prev_tab%>%
  arrange(item)


compareChisqPerSymptomPANSS <- function(bound, cur_question) {

  llm_data <- bound %>% 
    filter(item == cur_question
    )
  zi_dat <- bound %>% 
    filter(item == cur_question, 
           group == "CIMH Cohort")
  
  llm_list <- c("LLM 1", "LLM 2", "LLM 3")
  chi_results <- lapply(llm_list, function(llm_name) {
    print(llm_name)
    llm <- llm_data %>%
      filter(group == llm_name) 
    
    n_total <- sum(llm$n_present, llm$n_absence)
    
    
    cur_mat <- matrix(c(llm$n_present, llm$n_absence, 
                        zi_dat$n_present, zi_dat$n_absence),
                      nrow=2, byrow = T)
    print(cur_mat)
    
    
    
    cramers_v <- rcompanion::cramerV(cur_mat)[[1]]
    
    res <-chisq.test(cur_mat)
    df <- data.frame(item = cur_question,
                     llm = llm_name,
                     X_squared = res$statistic,
                     llm_perc_present = llm$n_present/n_total, 
                     spiller_perc_present = zi_dat$perc,
                     p_value = res$p.value, 
                     cramers_v = cramers_v
    )
    return(df)
    
  })
  
  
  chi_results <- do.call("rbind", chi_results)
  
  return(chi_results)
  
}



all_chisqs <- lapply(panss_vector,bound=summarized_panss, compareChisqPerSymptomPANSS)
all_chisqs <- do.call("rbind", all_chisqs)
all_chisqs$X_squared <- as.character(round(all_chisqs$X_squared, 2))
all_chisqs$p_value <- p.adjust(all_chisqs$p_value, method = "BH")
all_chisqs <- rename(all_chisqs, p_value_adj = p_value)
all_chisqs$p_value_adj <- format_pvals(all_chisqs$p_value_adj)
chisqs_wid <- pivot_wider(all_chisqs, id_cols = item, names_from = llm, values_from = c(X_squared, p_value_adj, cramers_v), 
                          names_vary = "slowest")

symp_prev_tab_comb <- merge(symp_prev_tab, chisqs_wid, by.x = "item", by.y = "item")

symp_prev_tab_comb<- symp_prev_tab_comb%>%
  arrange(item)

#write.csv(symp_prev_tab, file.path(saving_tables, "eTable10_SymptomPrevalencePANSS.csv"))
write.csv(symp_prev_tab_comb, file.path(saving_tables, "eTable14_SymptomPrevalencePANSS.csv"))


### Socioeconomic numbers
data <- read.csv(file.path(processed_folder, "main_dataset_v1.csv"))
data$llm <- factor(data$llm, levels = c("LLM 1", "LLM 2", "LLM 3"))
data$group <- factor(data$group, mental_disorders_short)

data %>%
  add_count(llm, name = "n_model") %>%  # adds n_model per llm group
  group_by(llm, race_ethnicity) %>%
  summarize(n = n(),
            perc = 100 * n / first(n_model),
            .groups = "drop") %>% 
  write.csv(file.path(saving_tables, "OTHER_RaceEthnicity.csv"))



data %>% 
  add_count(llm,group, name = "n_model") %>%  # adds n_model per llm group
  group_by(llm, employment_status, group) %>% 
  summarize(n = n(),
            perc = 100 * n / first(n_model),
            .groups = "drop") %>% 
  write.csv(file.path(saving_tables, "OTHER_Emplyoment.csv"))


data %>% 
  group_by(income)%>%
  summarize(n = n()) %>% 
  mutate(total = sum(n), 
         perc = 100*n/ total
         ) %>%
  write.csv(file.path(saving_tables, "OTHER_Income_2.csv"))

  

data %>% 
  add_count(llm,group, name = "n_model") %>%  # adds n_model per llm group
  group_by(llm, income, group) %>% 
  summarize(n = n(),
            perc = 100 * n / first(n_model),
            .groups = "drop") %>% 
  write.csv(file.path(saving_tables, "OTHER_Income.csv"))


data %>% 
  add_count(llm,group, name = "n_model") %>%  # adds n_model per llm group
  group_by(llm,group, health_insurance_status) %>% 
  summarize(n = n(),
            perc = 100 * n / first(n_model),
            .groups = "drop") %>% 
  write.csv(file.path(saving_tables, "OTHER_healthinsurancestatus.csv"))


data %>% 
  add_count(llm,group, name = "n_model") %>%  # adds n_model per llm group
  group_by(llm,group, smoking) %>% 
  summarize(n = n(),
            perc = 100 * n / first(n_model),
            .groups = "drop") %>%
  write.csv(file.path(saving_tables, "OTHER_smoking_status.csv"))



