#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

library(RSNNS)

# based on
# http://cran.r-project.org/web/packages/RSNNS/RSNNS.pdf
#
# Available functions/parameters can be viewed via getSnnsRFunctionTable()
#
do.rsnns <- function(tdf, network="mlp", testindex=NULL, printModel=FALSE) {
    seed <- 1
    setSnnsRSeedValue(seed)

    # define train set
    target <- tdf$target
    train.df <- drop(tdf, c("id", "target"))

    # make targets as labels
    targets <- decodeClassLabels(target)
    # split data for training and validation
    data <- splitForTrainingAndTest(train.df, targets, ratio=0.15)
    data <- normTrainingAndTestSet(data)

    # run NN algorithm
    x <- data$inputsTrain
    y <- data$targetsTrain
    net_size <- c(5) # one layer with 100 neurons, c(100, 100) two layers with 100 neurons
    net_iter <- 100
    model <- NULL
    linOut <- FALSE # use FALSE for classification, use TRUE for regression
    print(sprintf("Use %s network, %s for training, %s for validation", network, nrow(x), nrow(data$targetsTest)))
    if  (network=="mlp") {
        # MLP network
        # hidden functions: Act_Softmax, Act_TanH, Act_Logistic
        model <- mlp(x, y, size=net_size, maxit=net_iter,
                     initFunc="Randomize_Weights",
                     initFuncParams=c(-0.1, 0.1), learnFunc="Std_Backpropagation",
                     learnFuncParams=c(0.1, 0.01), updateFunc="Topological_Order",
                     updateFuncParams=c(0), hiddenActFunc="Act_Logistic",
#                     inputsTest=data$inputsTest, targetsTest=data$targetsTest,
                     shufflePatterns=TRUE, linOut=linOut)
    } else if(network=="rbf") {
        # RBF network
        model <- rbf(x, y, size=net_size, maxit=net_iter,
                     initFunc="RBF_Weights", initFuncParams=c(0,1, 0, 0.02, 0.04),
                     learnFunc="RadialBasisLearning", learnFuncParams=c(1e-05, 0, 1e-05, 0.1, 0.8),
                     updateFunc="Topological_Order", updateFuncParams=c(0),
#                     inputsTest=data$inputsTest, targetsTest=data$targetsTest,
                     shufflePatterns=TRUE, linOut=linOut)
    } else if(network=="jordan") {
        # jordan network
        model <- jordan(x, y, size=net_size, maxit=net_iter,
                     initFunc="JE_Weights", initFuncParams=c(1, -1, 0.3, 1, 0.5),
                     learnFunc="JE_BP", learnFuncParams=c(0.2),
                     updateFunc="JE_Order", updateFuncParams=c(0),
#                     inputsTest=data$inputsTest, targetsTest=data$targetsTest,
                     shufflePatterns=TRUE, linOut=linOut)
    } else if(network=="elman") {
        # elman network
        model <- elman(x, y, size=net_size, maxit=net_iter,
                     initFunc="JE_Weights", initFuncParams=c(1, -1, 0.3, 1, 0.5),
                     learnFunc="JE_BP", learnFuncParams=c(0.2),
                     updateFunc="JE_Order", updateFuncParams=c(0),
#                     inputsTest=data$inputsTest, targetsTest=data$targetsTest,
                     shufflePatterns=TRUE, linOut=linOut)
    }
    if(printModel==TRUE) print(model)

    # print confusion matrix over validation set
    predictions <- predict(model, data$inputsTest)
    ndf=sapply(as.data.frame(predictions), function(x) {return(round(x))})
    conf.matrix(data$targetsTest, ndf, printTable=T)

    # this code defines total index length to use based on target values
    # if target values starts with zero then we use max.target+1
    # otherwise max.target
    min.target <- min(target)
    max.target <- max(target)
    tot <- max.target
    if (min.target == 0) {
        tot <- max.target+1
    }
    pdf("rsnns.pdf")
    par(mfrow=c(2,2))
    for(idx in 1:tot)
        plotROC(predictions[,idx], data$targetsTest[,idx])
    plotIterativeError(model)
    dev.off()

    return(model)
}
