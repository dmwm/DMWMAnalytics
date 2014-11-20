#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# Start the clock!
ptm <- proc.time()

# default values
clf <- 'rsnns'
full <- FALSE
pred <- FALSE
train.name <- 'train.csv'
test.name <- 'test.csv'
script.dir <- getwd()
#script.dir <- dirname(sys.frame(1)$ofile)

# read and parse input args
cmd_args <- commandArgs()
for (arg in cmd_args) {
    arg <- as.character(arg)
    match <- grep("^--clf", arg)
    if (length(match) == 1) clf <- gsub("--clf=", "", arg)
    match <- grep("^--full", arg)
    if (length(match) == 1) full <- TRUE
    match <- grep("^--pred", arg)
    if (length(match) == 1) pred <- TRUE
    match <- grep("^--train", arg)
    if (length(match) == 1) train.name <- gsub("--train=", "", arg)
    match <- grep("^--test", arg)
    if (length(match) == 1) test.name <- gsub("--test=", "", arg)
    match <- grep("^--script-dir", arg)
    if (length(match) == 1) script.dir <- gsub("--script-dir=", "", arg)
}
print(sprintf("Classifier: %s, fullset: %s", clf, full))

# read helper code
source(paste0(script.dir, "helper.R"))

# reset previous graphics settings and close all plot windows
graph.reset()

read.data <- function(file.name) {
    xdf <- read.csv(paste0(getwd(), file.name), header=T)
    return(xdf)
}

# list of fields which we'll drop from train/test datasets
# to determine this list we used correlation matrix plot
drops <- c()

cat("Drops: ")
cat(drops, sep=", ")
cat("\n")

# load train data
file.name <- "train.csv"
train.df <- read.data(file.name)
#make.cor.plot(train.df)
train.df <- drop(train.df, drops)

print(sprintf("##### train.df %s #####", file.name))
names(train.df)
print(nrow(train.df))

# load test data
file.name <- "test.csv"
test.df <- read.data(file.name)
test.df <- drop(test.df, drops)

print(sprintf("##### test.df %s #####", file.name))
names(test.df)
print(nrow(test.df))

# always set a seed
set.seed(12345)

# what to keep, NULL means everything
keeps <- names(train.df)
cat("Attributes: ")
cat(keeps, sep=", ")
cat("\n")

# which formula to use, NULL means "target~."
formula <- NULL

# NP: set testindex if I'll use full dataset for training, otherwise
##### provide some random index to split trainset
if (full==F) {
    host <- Sys.getenv("HOST")
    print(sprintf("Run on '%s' host", host))
    if (host=="") { # we run on local node
        index <- 1:nrow(train.df)
        testindex <- sample(index, trunc(length(index)/2)) # use short train.df to speed up the process
        train.df <- train.df[testindex,]
    }
    # define index to split data into train/validation sets
    index <- 1:nrow(train.df)
    testindex <- sample(index, trunc(length(index)/3))
} else {
    testindex <- NULL
}

print("Head of train.df")
print(head(train.df))

# Run R ML algorithms
source(paste0(script.dir, "ada.R"))
source(paste0(script.dir, "gbm.R"))
source(paste0(script.dir,"svm.R"))
source(paste0(script.dir,"ksvm.R"))
source(paste0(script.dir,"rf.R"))
source(paste0(script.dir,"nnet.R"))
source(paste0(script.dir,"rbm.R"))
source(paste0(script.dir,"naiveBayes.R"))

print(sprintf("##### Run %s-classifier #####", clf))
if (clf=="svm") {
    fit <- do.svm(train.df, formula=formula, testindex=testindex, printModel=T)
} else if (clf=="ksvm") {
    fit <- do.ksvm(train.df, formula=formula, testindex=testindex, printModel=T)
} else if (clf=="rf") {
    fit <- do.rf(train.df, formula=formula, testindex=testindex, printModel=T)
} else if (clf=="ada") {
    fit <- do.ada(train.df, formula=formula, testindex=testindex, printModel=T)
} else if (clf=="gbm") {
    fit <- do.gbm(train.df, formula=formula, testindex=testindex, printModel=T)
} else if (clf=="nb") {
    fit <- do.nb(train.df, formula=formula, testindex=testindex, printModel=T)
} else if (clf=="rsnns") {
    network <- 'mlp'
    fit <- do.rsnns(train.df, network=network, testindex=testindex, printModel=T)
} else if (clf=="rbm") {
    fit <- do.rbm(train.df, testindex=testindex, printModel=T)
} else {
    print(sprintf("Unsupported classifier: %s", clf))
}

# get prediction and write them to the file
if (pred==T) {
    print(sprintf("### Run prediction ###"))
    pfile <- sprintf("pred.txt")
    ids <- test.df$id
    test.df <- drop(test.df, c("id"))
    if (clf=="rsnns") {
        predictions <- predict(fit, normalizeData(test.df))
    } else if(clf=="ksvm") {
        predictions <- predict(fit, test.df, type="probabilities")
    } else if(clf=="rf" || clf=="ada") {
        predictions <- predict(fit, test.df, type="prob")
    } else if(clf=="gbm") {
        predictions <- predict(fit, test.df, type="response", n.trees=150)
    } else {
        predictions <- predict(fit, test.df)
    }
    print(sprintf("# ids: %s, # predicitons: %s", length(ids), length(predictions)))
    print(head(ids))
    print(head(predictions))

    for(idx in 1:2) {
        odf <- data.frame(id=ids, repeatProbability=predictions[,idx])
        # remove duplicate based on id and keep row with max probability value
        xdf=aggregate(odf, by=list(odf$id), function(x) max(x))
        xdf <- drop(xdf, c("Group.1"))
        write.table(xdf, pfile, row.names=F, col.names=F, sep=',')

        cmd <- "echo \"id,repeatProbability\" > p.txt"
        system(cmd)
        cmd <- sprintf("cat p.txt pred.txt > predictions%s.txt", idx)
#        cmd <- "cat p.txt pred.txt > predictions.txt"
        system(cmd)
        system("rm pred.txt p.txt")
    }
}

#source("R/caret.R")
# Load caret stuff, here how it should be used (default alg is "rf"):
#      run.caret(train.df)
#      run.caret(train.df, "ksvm")
# uncomment loop below when you want to test multiple MLs via caret
#for(m in c("rf", "svmRadial", "svmLinear", "svmPoly")) {
#    print(sprintf("Run caret with %s", m))
#    run.caret(train.df, m)
#}

# Stop the clock
print(proc.time() - ptm)
