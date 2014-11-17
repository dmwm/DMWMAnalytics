#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

# based on
# http://cran.r-project.org/web/packages/e1071/e1071.pdf
# http://hosho.ees.hokudai.ac.jp/~kubo/Rdoc/library/e1071/html/naiveBayes.html
do.nb <- function(tdf, formula=NULL, testindex=NULL, printModel=FALSE, laplace=NULL) {

    # split data if requisted into train and validation sets
    if (is.null(testindex)) {
        train.df <- tdf
        print(sprintf("Run NaiveBayes, use full training set"))
    } else {
        valid.df <- tdf[testindex,]
        train.df <- tdf[-testindex,]
        print(sprintf("Run NaieveBayes, train %d, valid %d", nrow(train.df), nrow(valid.df)))
    }
    target <- train.df$target

    # exclude id columns to work with ML
    train.df <- drop(train.df, c("id"))

    # run svm algorithm
    if (is.null(formula)) formula <- as.formula("target~.")
    if (is.null(laplace)) {
        model <- naiveBayes(formula, data=train.df)
    } else {
        model <- naiveBayes(formula, data=train.df, laplace=laplace)
    }
    if(printModel==TRUE) print(model)

    # print confusion matrix over validation set
    target <- valid.df$target
    valid.df <- drop(valid.df, c("id", "target"))
    pred <- predict(model, valid.df)
    conf.matrix(target, pred, printTable=printModel)

    return(model)

}
