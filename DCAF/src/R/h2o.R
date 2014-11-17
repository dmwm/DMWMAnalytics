#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# load data
my.path <- paste0(getwd(), "/")
# example
# load.data <- read.csv(paste0(my.path, file.name), header=TRUE)

# set seed
set.seed(12345)

library(h2o)

localH2O = h2o.init(ip = "127.0.0.1", port = 54321, startH2O = TRUE)
train.file = "/opt/data/AcquireValuedShoppersChallenge/copy/train.vw.csv"
data.hex = h2o.importFile(localH2O, path = train.file, key = "data.hex")
# read data from train file and get list of attributes by excluding first/last (id/target)
df = read.csv(train.file, header=T, nrow=2)
attrs = names(df)
attrs = attrs[-c(1, length(attrs))]
# build model
model = h2o.gbm(y="target", x=attrs, data=data.hex)
pred = h2o.predict(model)
head(pred)
