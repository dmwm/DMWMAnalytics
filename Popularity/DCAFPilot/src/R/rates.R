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
libs <- c("ggplot2", "plyr", "dplyr", "gridExtra")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

df=read.csv('wdir/data.csv', header=F)
names(df)=c("week","tier","tp","tn","fp","fn")
df=subset(df, df$tier!="MINIAODSIM")
p1=ggplot(df, aes(x=week, y=tp, colour=tier)) + geom_line()
p2=ggplot(df, aes(x=week, y=tn, colour=tier)) + geom_line()
p3=ggplot(df, aes(x=week, y=fp, colour=tier)) + geom_line()
p4=ggplot(df, aes(x=week, y=fn, colour=tier)) + geom_line()

pdf(sprintf("rates.pdf"))
grid.arrange(p1, p2, p3, p4, ncol=2, main=sprintf("TP/TN/FP/FN rates"))
dev.off()
