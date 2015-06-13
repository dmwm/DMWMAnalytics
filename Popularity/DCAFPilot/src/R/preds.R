#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# load data
my.path <- paste0(getwd(), "/")
# example
# load.data <- read.csv(paste0(my.path, file.name), header=TRUE)

# set seed
set.seed(12345)

# load libraries
libs <- c("ggplot2", "gridExtra")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

df = read.csv('data.csv', header=T)

clfs=c("xgb","RandomForest","SGDClassifier","LinearSVC")
for(clf in clfs) {
    ndf = subset(df, df$clf==clf)
    if(clf=="xgb") fcolor="lightblue"
    else if(clf=="RandomForest") fcolor="lightgreen"
    else if(clf=="SGDClassifier") fcolor="magenta"
    else fcolor="grey"

    p1 = ggplot(ndf, aes(x=tier, y=tp)) + theme_bw() +
         geom_bar(stat="identity", fill=fcolor) + scale_y_continuous(limits=c(0,100)) +
         theme(axis.text.x = element_text(angle=30, hjust=1, vjust=1)) +
         theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
         theme(panel.grid.major.y = element_blank(), panel.grid.minor.y = element_blank()) +
         ggtitle("True Positives") + ylab("Percentage")
    p2 = ggplot(ndf, aes(x=tier, y=tn)) + theme_bw() +
         geom_bar(stat="identity", fill=fcolor) + scale_y_continuous(limits=c(0,100)) +
         theme(axis.text.x = element_text(angle=30, hjust=1, vjust=1)) +
         theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
         theme(panel.grid.major.y = element_blank(), panel.grid.minor.y = element_blank()) +
         ggtitle("True Negatives") + ylab("Percentage")
    p3 = ggplot(ndf, aes(x=tier, y=fp)) + theme_bw() +
         geom_bar(stat="identity", fill=fcolor) + scale_y_continuous(limits=c(0,100)) +
         theme(axis.text.x = element_text(angle=30, hjust=1, vjust=1)) +
         theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
         theme(panel.grid.major.y = element_blank(), panel.grid.minor.y = element_blank()) +
         ggtitle("False Positives") + ylab("Percentage")
    p4 = ggplot(ndf, aes(x=tier, y=fn)) + theme_bw() +
         geom_bar(stat="identity", fill=fcolor) + scale_y_continuous(limits=c(0,100)) +
         theme(axis.text.x = element_text(angle=30, hjust=1, vjust=1)) +
         theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
         theme(panel.grid.major.y = element_blank(), panel.grid.minor.y = element_blank()) +
         ggtitle("False Negatives") + ylab("Percentage")
    print(sprintf("Plot: %s", clf))
    pdf(sprintf("%s.pdf", clf))
    grid.arrange(p1, p2, p3, p4, ncol=2, main=sprintf("%s classifier", clf))
    dev.off()
#    ggsave(sprintf("%s.pdf", clf))
}
