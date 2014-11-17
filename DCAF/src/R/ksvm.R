#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

do.ksvm <- function(tdf, formula=NULL, testindex=NULL, printModel=FALSE,
                        sigma=1, cost=1) {
    # split data if requisted into train and validation sets
    if (is.null(testindex)) {
        train.df <- tdf
        print(sprintf("Run KSVM, use full training set"))
    } else {
        valid.df <- tdf[testindex,]
        train.df <- tdf[-testindex,]
        print(sprintf("Run KSVM, train %d, valid %d", nrow(train.df), nrow(valid.df)))
    }
    target <- train.df$target

    # exclude id columns to work with ML
    train.df <- drop(train.df, c("id"))

    ###### kernels

    # PolyKernels
    poly <- polydot(degree=1, scale=1, offset=0)
    # RBF kernels
    sigma <- sigma
    rbf <- rbfdot(sigma=sigma)

    # kernel choice
    k <- rbf

    # type of classification
    type <- sprintf("C-svc")
    cross <- 10

    # run svm algorithm
    if (is.null(formula)) formula <- as.formula("target~.")
    model <- ksvm(formula, data=train.df,
                type=type, cross=cross, kernel=k, C=cost, prob.model=T)
    if(printModel==TRUE) print(model)

    # print confusion matrix over validation set
    target <- valid.df$target
    valid.df <- drop(valid.df, c("id", "target"))
    pred <- predict(model, valid.df)
    conf.matrix(target, pred, printTable=printModel)

    return(model)
}
