# load libraries
libs <- c("stats", "corrplot", "ggplot2", "randomForest", "e1071", "kernlab", "RSNNS", "caret", "verification")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

# set seed
set.seed(12345)

source(paste0(script.dir, "plot_helpers.R"))

### Helper function
download <- function(url, dir="./data") {
    dir.create(dir, showWarnings = FALSE)
    dest.file <- paste(dir, digest(url, algo="md5"), sep="/")
    if  (!file.exists(dest.file)) {
        cat("download url", url, "\n")
        download.file(url, dest=dest.file)
    }
    return(dest.file)
}

# helper function to order data frame for given set of attributes
df.order <- function(x, x.order) {
    d <- x[with(x, order(x.order)), ]
    return(d)
}

# helper function to drop columns from given dataset
drop <- function(xdf, drops) {
    return(xdf[,!names(xdf) %in% drops])
}
# helper function to drop columns from given dataset
keep <- function(xdf, keeps) {
    return(xdf[,names(xdf) %in% keeps])
}

# helper function to get sample index for given dataframe
# then someone can divided training/test set into the following:
#    testset <- df[testindex,]
#    trainset <- df[-testindex,]
sample.index <- function(x) {
    # this is an example on how to split data into train/test datasets
    index <- 1:nrow(x)
    testindex <- sample(index, trunc(length(index)/3))
    return(testindex)
}

# helper function to dump on stdout rows with NA
na.rows <- function(x) {
    print(unique(is.na(x)))
}

# helper function to calculate error of predicion
pred.error <- function(obs, pred) {
    error <- sqrt((sum((obs-pred)^2))/length(obs))
    return(error)
}

# convert predicition vector into vector of ints
int.pred <- function(p) {
    # convert pred into integers
    pred <- sapply(p, function(x) {as.integer(as.character(x))})
    return(pred)
}

# Helper function for AUC numbers
auc <- function(obs, pred) {
    aobj <- roc.area(obs, pred)
    msg <- sprintf("AUC: %s, p-value: %s", aobj$A, aobj$p.value)
    print(msg)
}

# Helper fuction to build and print confution matrix for given observeraion and
# prediction variables
conf.matrix <- function(obs, pred, printTable=TRUE) {
    # use caret library to make confusion matrix per each column
    for(idx in 1:ncol(pred)) {
        levels <- sort(unique(c(unique(pred[,idx]), unique(obs[,idx]))))
        pred.values <- factor(pred[,idx], levels=levels)
        obs.values <- factor(obs[,idx], levels=levels)
        xtab <- table(pred.values, obs.values)
        cm <- caret::confusionMatrix(xtab)
        vals <- as.data.frame(t(as.data.frame(cm$overall)))
        msg <- sprintf("Column %s accuracy %f kappa %f", idx, vals$Accuracy, vals$Kappa)
        print(cm)
        print(msg)
    }
    # build confusion matrix for all values
    obs <- int.pred(obs)
    pred <- int.pred(pred)
    tab <- table(observed = obs, predicted = pred)
    cls <- classAgreement(tab)
    if(printTable==TRUE) print(tab)
    err <- pred.error(obs, pred)
    msg <- sprintf("Correctly classified: %f kappa %f error %f", cls$diag, cls$kappa, err)
    print(msg)
}

# merge prediction
merge.pred <- function(fits.df, printTable=TRUE) {
    pids <- fits.df$pid
    obs <- fits.df$Survived
    pred <- rowSums(fits.df[3:ncol(fits.df)])/2
    pred <- sapply(pred, function(x) {if(x==0.5) return(1) else return(as.integer(x))})
    conf.matrix(obs, pred, printTable)
}

# helper function to print misclassified rows
misclassified <- function(xdf, pred) {
    ndf <- data.frame()
    for(i in 1:nrow(xdf)) {
        row <- xdf[i,]
        if(row$Survived != pred[i]) {
            ndf <- rbind(ndf, row)
        }
    }
    print(ndf)
    print(sprintf("Misclassified: %d", nrow(ndf)))
}

roc <- function(fit, df, fname) {
    pr <- predict(fit, newdata=df, type="prob")[,2]
    pred <- prediction(pr, df$Survived)

    # get performance data for various parameters, e.g. sensitivity, etc.
    perf.ss <- performance(pred, "sens", "spec")
    perf.roc <- performance(pred, "tpr", "fpr")
    perf.lift <- performance(pred, "lift", "rpp")
    perf.pp <- performance(pred, "prec", "rec")
    perf.auc <- performance(pred, "auc")

    # make final plot of performance data
    fig.name <- paste0(fname, ext)
    start.plot(fig.name)
    par(mfrow=c(2,2))
    plot(perf.roc)
    plot(perf.ss)
    plot(perf.pp)
    plot(perf.lift)
    dev.off()
}
