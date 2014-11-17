#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

# based on
# http://cran.r-project.org/web/packages/randomForest/randomForest.pdf
do.rf <- function(tdf, formula=NULL, testindex=NULL, printModel=FALSE) {

    # split data if requisted into train and validation sets
    if (is.null(testindex)) {
        train.df <- tdf
        print(sprintf("Run RandomForest, use full training set"))
    } else {
        valid.df <- tdf[testindex,]
        train.df <- tdf[-testindex,]
        print(sprintf("Run RandomForest, train %d, valid %d", nrow(train.df), nrow(valid.df)))
    }
    target <- train.df$target

    # exclude id columns to work with ML
    train.df <- drop(train.df, c("id"))

    # run RandomForest, make sure that the variable used for classification is a
    # factor. For prediction use the same dataset but exclude classification var.
    if (is.null(formula)) formula <- as.formula("target~.")
    model <- randomForest(formula, data=train.df, importance=T, ntree=50)
    if(printModel==TRUE) print(model)

    # print confusion matrix over validation set
    target <- valid.df$target
    valid.df <- drop(valid.df, c("id", "target"))
    pred <- predict(model, valid.df)
    conf.matrix(target, pred, printTable=printModel)

    return(model)
}
