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
libs <- c("corrplot", "ggplot2", "randomForest", "e1071", "caret", "data.table", "plyr", "dplyr")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

# pie chart for popular statistics
# naccess>10

pdf(sprintf("naccess2014.pdf"))
slices <- c(8, 32, 1.3, 49, 9.7)
lbls <- c("AOD", "AODSIM", "MINIAOD", "USER", "OTHER")
pct <- round(slices/sum(slices)*100)
lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls,"%",sep="") # ad % to labels 
pie(slices,labels = lbls, col=rainbow(length(lbls)),
  	main="2014 data naccess>10")
dev.off()

pdf(sprintf("nusers2014.pdf"))
slices <- c(35, 42, 0.8, 10, 12.2)
lbls <- c("AOD", "AODSIM", "MINIAOD", "USER", "OTHER")
pct <- round(slices/sum(slices)*100)
lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls,"%",sep="") # ad % to labels 
pie(slices,labels = lbls, col=rainbow(length(lbls)),
  	main="2014 data log(nuser)>2")
dev.off()

pdf(sprintf("nocut2014.pdf"))
slices <- c(7.25, 31, 1.5, 50, 10.25)
lbls <- c("AOD", "AODSIM", "MINIAOD", "USER", "OTHER")
pct <- round(slices/sum(slices)*100)
lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls,"%",sep="") # ad % to labels 
pie(slices,labels = lbls, col=rainbow(length(lbls)),
  	main="2014 data no cut")
dev.off()

