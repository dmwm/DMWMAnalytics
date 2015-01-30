#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# default values
train.file <- FALSE
valid.file <- FALSE

# read and parse input args
cmd_args <- commandArgs()
for (arg in cmd_args) {
    arg <- as.character(arg)
    match <- grep("^--train", arg)
    if (length(match) == 1) train.file <- gsub("--train=", "", arg)
    match <- grep("^--valid", arg)
    if (length(match) == 1) valid.file <- gsub("--valid=", "", arg)
}

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

df=filter(fread(train.file), target>0)
ndf=filter(fread(valid.file), target>0)
old.datasets=unlist(lapply(ndf$dataset, function(d) {if((d %in% df$dataset)==TRUE) return(d)}))
new.datasets=unlist(lapply(ndf$dataset, function(d) {if((d %in% df$dataset)==FALSE) return(d)}))
write.csv(data.frame(id=new.datasets), gzfile("new_datasets.csv.gz"),row.names=FALSE,quote=FALSE)
