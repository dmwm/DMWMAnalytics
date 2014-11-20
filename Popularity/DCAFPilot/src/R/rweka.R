#!/usr/bin/env Rscript

rm(list=ls())

# default values
clf <- 'RF'
full <- FALSE
mem <- "6g"
nrows <- FALSE

# read and parse input args
cmd_args <- commandArgs()
for (arg in cmd_args) {
    arg <- as.character(arg)
    match <- grep("^--clf", arg)
    if (length(match) == 1) clf <- gsub("--clf=", "", arg)
    match <- grep("^--mem", arg)
    if (length(match) == 1) mem <- gsub("--mem=", "", arg)
    match <- grep("^--full", arg)
    if (length(match) == 1) full <- TRUE
    match <- grep("^--nrows", arg)
    if (length(match) == 1) nrows <- as.numeric(gsub("--nrows=", "", arg))
}
print(sprintf("Classifier: %s", clf))

# set seed
set.seed(12345)

# increase Java heap size
# http://www.bramschoenmakers.nl/en/node/726
java_mem <- sprintf("-XX:-UseGCOverheadLimit -Xmx%s", mem)
options( java.parameters = java_mem )
library(RWeka)
source("R/helper.R")

csvTrainfile <- "data/train.vw.csv"
csvTestfile <- "data/test.vw.csv"

drops <- c("id")

cat("Drops: ")
cat(drops, sep=", ")
cat("\n")

if(nrows!=F) {
    training <- read.csv(csvTrainfile, header=T, nrow=nrows)
} else {
    training <- read.csv(csvTrainfile, header=T)
}
xTrain <- drop(training, drops)

test <- read.csv(csvTestfile, header=T)
ids <- test$id
xTest <- drop(test, drops)

# split data for training and validation
if(full==T) {
    train.df <- xTrain
    targets=train.df$target
    train.df$target=as.factor(train.df$target)
    print(sprintf("Use full train sample %s", nrow(train.df)))
} else {
    index <- 1:nrow(xTrain)
    testindex <- sample(index, trunc(length(index)/3))
    valid.df <- xTrain[testindex,]
    targets=valid.df$target
    valid.df$target=as.factor(valid.df$target)
    print(sprintf("valid.df %s", nrow(valid.df)))
    train.df <- xTrain[-testindex,]
    train.df$target=as.factor(train.df$target)
    print(sprintf("train.df %s", nrow(train.df)))
}

print(sprintf("Train model"))

print(sprintf("##### Run %s-classifier #####", clf))
# classifier objects
RF <- make_Weka_classifier("weka/classifiers/trees/RandomForest")
NB <- make_Weka_classifier("weka/classifiers/bayes/NaiveBayes")
BNet <- make_Weka_classifier("weka/classifiers/bayes/BayesNet")
LWL <- make_Weka_classifier("weka/classifiers/lazy/LWL")
# classifier's parameters can be found via
# WOW(CLF) call, e.g. WOW(J48)
if (clf=="LogitBoost") {
    # Q=TRUE use resampling instead of re-weighting
    # F=<value> Number of folds for internal cross-validation, default 0 -- no cross-validation
    # R=<value> Number of runs for internal cross-validation, default 1
    #model <- LogitBoost(target~., data=train.df, control = Weka_control(F=10,R=1,Q=TRUE))
    #model <- LogitBoost(target~., data=train.df, control = Weka_control(F=10,R=10))
    #model <- LogitBoost(target~., data=train.df, control = Weka_control(F=10,R=2,Q=TRUE))
    model <- LogitBoost(target~., data=train.df)
} else if(clf=="Logistic") {
    model <- Logistic(target~., data=train.df)
} else if(clf=="LWL") {
    model <- LWL(target~., data=train.df)
} else if(clf=="J48") {
    model <- J48(target~., data=train.df)
} else if(clf=="JRip") {
    model <- JRip(target~., data=train.df)
} else if(clf=="M5Rules") {
    model <- M5Rules(target~., data=train.df)
} else if(clf=="LMT") {
    model <- LMT(target~., data=train.df)
} else if(clf=="PART") {
    model <- PART(target~., data=train.df)
} else if(clf=="OneR") {
    model <- OneR(target~., data=train.df)
} else if(clf=="KMeans") {
    model <- SimpleKMeans(train.df[,-ncol(train.df)], Weka_control(N=2))
} else if(clf=="Bagging") {
    model <- Bagging(target~., data=train.df)
} else if(clf=="LBR") {
    # LBR ("Lazy Baysesian Rules")
    model <- LBR(target~., data=train.df)
} else if(clf=="SMO") {
    # V=<value> The number of folds for the internal cross-validation.
    # L=<value> The tolerance parameter. (default 1.0e-3)
    # M=TRUE Fit logistic models to SVM outputs.
    # K=<value> The Kernel to use.  (default: weka.classifiers.functions.supportVector.PolyKernel)
    # K=list("RBFKernel", G = 2)
    kernel=list("weka.classifiers.functions.supportVector.RBFKernel", G=0.1)
    #model <- SMO(target~., data=train.df, control = Weka_control(V=10))
    model <- SMO(target~., data=train.df, control = Weka_control(V=10,K=kernel))
#    model <- SMO(target~., data=train.df)
} else if(clf=="RF") {
    model <- RF(target~., data=train.df, control = Weka_control(I=10,K=0))
} else if(clf=="Stacking") {
    weka_control = Weka_control(M="weka.classifiers.bayes.NaiveBayes",B=list(J48, M=2),B=list(RF, I=10))
    model <- Stacking(target~., data=train.df, control=weka_control)
} else if(clf=="CostSensitiveClassifier") {
    model <- CostSensitiveClassifier(target~., data=train.df)
} else if(clf=="NaiveBayes") {
    model <- NB(target~., data=train.df)
} else if(clf=="BayesNet") {
    model <- BNet(target~., data=train.df)
} else if(clf=="BayesNetRepHC") {
    Est="weka.classifiers.bayes.net.estimate.SimpleEstimator"
    Alg="weka.classifiers.bayes.net.search.global.RepeatedHillClimber"
#    wcontrol=c("-Q", Alg, "--", "-U", 10, "-P", 2, "-R", "-S", "k-Fold-CV", "-mbc", "-E", Est)
    wcontrol=c("-Q", Alg, "--", "-U", 10, "-S", "k-Fold-CV", "-E", Est)
    clf=sprintf("BayesNetRepHC")
    model <- BNet(target~., data=train.df, control=wcontrol)
} else if(clf=="BayesNetK2") {
    Est="weka.classifiers.bayes.net.estimate.SimpleEstimator"
    Alg="weka.classifiers.bayes.net.search.global.K2"
    wcontrol=c("-Q", Alg, "--", "-P", 2, "-R", "-S", "AIC", "-mbc", "-E", Est)
    clf=sprintf("BayesNetK2")
    model <- BNet(target~., data=train.df, control=wcontrol)
#    Alg="weka.classifiers.bayes.net.search.local.LAGDHillClimber"
#    wcontrol=c("-Q", Alg, "--", "-L", 2, "-G", 10, "-P", 2, "-S", "AIC", "-mbc", "-E", Est)
#    clf=sprintf("BayesNetLagDHillClimber")
    #Alg="weka.classifiers.bayes.net.search.local.GeneticSearch"
    #Alg="weka.classifiers.bayes.net.search.local.SimulatedAnnealing"
    #Alg="weka.classifiers.bayes.net.search.local.LocalScoreSearchAlgorithm"
    #Alg="weka.classifiers.bayes.net.search.local.TAN"
    #Alg="weka.classifiers.bayes.net.search.local.TabuSearch"
} else if(clf=="Ada") {
    model <- AdaBoostM1(target~., data=train.df, control = Weka_control(W = list(J48, M = 30)))
}

print(sprintf("Trained model"))
print(model)
if(full==T) {
    preds <- as.data.frame(predict(model, train.df, type = "prob"))
} else {
    preds <- as.data.frame(predict(model, valid.df, type = "prob"))
}
pred <- preds[,ncol(preds)]
auc(targets, pred)

## write a submission file
preds <- as.data.frame(predict(model, xTest, type = "prob"))
pred <- preds[,ncol(preds)]
zz <- gzfile(sprintf("weka_%s_pred.csv.gz", clf), "wt")
write.table(data.frame(id=ids, repeatProbability=pred), zz, sep=",", quote = FALSE, row.names=FALSE)
close(zz)

#quit(save = "no")
