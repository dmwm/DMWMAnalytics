#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

library(MASS)

do.lda <- function(tdf, keeps=NULL, formula=NULL, testindex=NULL, printModel=FALSE) {
    # keep requested attributes
    if(!is.null(keeps)) tdf <- keep(tdf, keeps)

    # split data if requisted into train and validation sets
    if (is.null(testindex)) {
        train.df <- tdf
        print(sprintf("Run LDA, use full training set"))
    } else {
        valid.df <- tdf[testindex,]
        train.df <- tdf[-testindex,]
        print(sprintf("Runi LDA, train %d, valid %d", nrow(train.df), nrow(valid.df)))
    }
    target <- train.df$target

    # exclude id columns to work with ML
    train.df <- drop(train.df, c("id"))

    # run lda algorithm
    if (is.null(formula)) formula <- as.formula("target~.")
    model <- lda(formula, data=train.df)
    if(printModel==TRUE) print(model)

    # print confusion matrix over validation set
    target <- valid.df$target
    valid.df <- drop(valid.df, c("id", "target"))
    pred <- predict(model, valid.df)
    conf.matrix(target, pred, printTable=printModel)

    return(model)
}
