#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# default values
file.name <- FALSE
out.file <- "/tmp/vw_cross.pdf"

# read and parse input args
cmd_args <- commandArgs()
for (arg in cmd_args) {
    arg <- as.character(arg)
    match <- grep("^--input", arg)
    if (length(match) == 1) file.name <- gsub("--input=", "", arg)
    match <- grep("^--output", arg)
    if (length(match) == 1) out.file <- gsub("--output=", "", arg)
}
if (file.name == FALSE) stop("Usage: vw_cross.R --input=<filename> --output=<filename>\n")

# load data
df <- read.csv(file.name, header=TRUE)
obs <- df$target
pred <- df$intpred
pred.prob <- df$predvalue

# load libraries
libs <- c("caret", "verification", "ROCR")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

# print confusion matrix
xtab <- table(pred, obs)
caret::confusionMatrix(xtab)

# print AUC value
aobj <- roc.area(obs, pred)
msg <- sprintf("AUC: %s, p-value: %s", aobj$A, aobj$p.value)
print(msg)

# plot ROC curve
pobj <- prediction(pred.prob, obs)
pdf(out.file)
par(mfrow=c(2,2))
perf <- performance(pobj,"tpr","fpr")
plot(perf)
perf <- performance(pobj, "prec", "rec")
plot(perf)
perf <- performance(pobj, "sens", "spec")
plot(perf)
perf <- performance(pobj, "lift", "rpp")
plot(perf)
dev.off()
