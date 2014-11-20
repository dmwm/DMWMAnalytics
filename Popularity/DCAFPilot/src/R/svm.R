#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

# based on
# http://cran.r-project.org/web/packages/e1071/e1071.pdf
do.svm <- function(tdf, formula=NULL, testindex=NULL, printModel=FALSE) {
    # split data if requisted into train and validation sets
    if (is.null(testindex)) {
        train.df <- tdf
        print(sprintf("Run SVM, use full training set"))
    } else {
        valid.df <- tdf[testindex,]
        train.df <- tdf[-testindex,]
        print(sprintf("Run SVM, train %d, valid %d", nrow(train.df), nrow(valid.df)))
    }
    target <- train.df$target

    # exclude id columns to work with ML
    train.df <- drop(train.df, c("id"))

    # kernels
    k <- sprintf('polynomial')
    degree <- 3
    gamma <- 1
    type <- sprintf('C-classification')
    cross <- 10

    # run svm algorithm (e1071 library) for given vector of data and kernel
    if (is.null(formula)) formula <- as.formula("target~.")
    model <- svm(formula, data=train.df,
                 type=type, cross=cross, kernel=k, gamma=gamma, degree=degree)
    if(printModel==TRUE) print(model)

    # print confusion matrix over validation set
    target <- valid.df$target
    valid.df <- drop(valid.df, c("id", "target"))
    pred <- predict(model, valid.df)
    conf.matrix(target, pred, printTable=printModel)

    return(model)
}
