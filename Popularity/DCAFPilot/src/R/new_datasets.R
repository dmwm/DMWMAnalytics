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
libs <- c("data.table", "bit64", "plyr", "dplyr")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

df=filter(fread('train_clf_cond.csv'), target>0)
ndf=filter(fread('valid_clf_cond.csv'), target>0)
old.datasets=unlist(lapply(ndf$dataset, function(d) {if((d %in% df$dataset)==TRUE) return(d)}))
new.datasets=unlist(lapply(ndf$dataset, function(d) {if((d %in% df$dataset)==FALSE) return(d)}))
write.csv(data.frame(id=new.datasets), gzfile("new_datasets.csv.gz"),row.names=FALSE,quote=FALSE)
