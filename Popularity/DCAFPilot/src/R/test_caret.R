#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# load data
my.path <- paste0(getwd(), "/")
# example
# load.data <- read.csv(paste0(my.path, file.name), header=TRUE)

# set seed
set.seed(12345)

library(caret)
library(bit64)
library(dplyr)
library(data.table)
library(randomForest)
library(ggplot2)

#train.df=read.csv('2014.10k_clf.csv.gz', header=T, nrows=1000)
train.df=fread('2014.10k_clf.csv')
train.df$target=as.factor(train.df$target)
ctrl <- trainControl(method="repeatedcv", repeats=5, classProbs = TRUE, summaryFunction=twoClassSummary)
model <- train(target ~ ., data = train.df, method="rf", metric="ROC", verbose=F, trControl=ctrl)
pdf("model.pdf")
ggplot(model) + theme(legend.position = "top")
dev.off()
