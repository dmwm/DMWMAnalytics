#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

# documentation
# http://cran.r-project.org/web/packages/caret/caret.pdf
source("R/helper.R")
library(doParallel)
library(caret)

set.seed(1)

# create parallel backend
#cl <- makeCluster(2)
#registerDoParallel(cl)

run.caret <- function(d, model="rf") {

x <- drop(d, c("id"))
x$target <- sapply(x$target, function(y) {as.factor(y)})
print(str(x))
inTrain <- createDataPartition(x$target, p = .75, list = FALSE)
trainDescr <- x[ inTrain, -ncol(x)]
testDescr  <- x[-inTrain, -ncol(x)]
trainClass <- x$target[ inTrain]
testClass  <- x$target[-inTrain]
method <- c("center", "scale")
procValues <- preProcess(trainDescr, method = method)
trainScaled <- predict(procValues, trainDescr)
testScaled  <- predict(procValues, testDescr)
m.fit <- train(x = trainDescr, y = trainClass,
                method = model, preProc = method,
                ## Length of default tuning parameter grid
                tuneLength = 8,
                ## Bootstrap resampling with custon performance metrics:
                ## sensitivity, specificity and ROC curve AUC
                trControl = trainControl(method = "repeatedcv", repeats = 5),
                metric = "Kappa",
                ## Pass arguments to ksvm
                fit = TRUE)
print(m.fit, printCall = FALSE)
print(class(m.fit))
print(sprintf("Final Model"))
print(class(m.fit$finalModel))
#par(mfrow=c(2,1))
#plot(m.fit, xTrans = function(x) log2(x))
#densityplot(m.fit, metric = "Kappa", pch = "|")

m.pred <- predict(m.fit, testDescr)
cm <- confusionMatrix(m.pred, testClass)
print(sprintf("Confusion Matrix"))
print(cm)

return(m.fit)

}
