#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# load data
my.path <- paste0(getwd(), "/")
# example
# load.data <- read.csv(paste0(my.path, file.name), header=TRUE)

# set seed
set.seed(12345)

library(data.table)
library(plyr)
library(dplyr)
library(bit64)

df <- fread('2014.10k.csv')

dbs.stat <- function(df, dbsid) {
#    tot <- nrow(filter(df, dbs==dbsid))
    tot <- length(filter(df, dbs==dbsid)$dataset)
    uni <- length(unique(filter(df, dbs==dbsid)$dataset))
#    tot_acc <- nrow(filter(df, dbs==dbsid & naccess==0))
    tot_acc <- length(filter(df, dbs==dbsid & naccess==0)$dataset)
    uni_acc <- length(unique(filter(df, dbs==dbsid & naccess==0)$dataset))
#    tot_nac <- nrow(filter(df, dbs==dbsid & naccess!=0))
    tot_nac <- length(filter(df, dbs==dbsid & naccess!=0)$dataset)
    uni_nac <- length(unique(filter(df, dbs==dbsid & naccess!=0)$dataset))
    print(sprintf("DBS-%s", dbsid))
    print(sprintf("total: %s %s %s", tot, tot_acc, tot_nac))
    print(sprintf("unique: %s %s %s", uni, uni_acc, uni_nac))
}

dbs.stat(df, 0)
dbs.stat(df, 1)
dbs.stat(df, 2)
dbs.stat(df, 3)
