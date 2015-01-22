#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# load data
my.path <- paste0(getwd(), "/")
# example
# load.data <- read.csv(paste0(my.path, file.name), header=TRUE)

# set seed
set.seed(12345)

# load libraries
libs <- c("corrplot", "ggplot2", "randomForest", "e1071", "caret", "data.table", "plyr", "dplyr")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

# http://onertipaday.blogspot.com/2011/07/word-cloud-in-r.html
library(RColorBrewer)
library(wordcloud)

csv_files <- list.files(path="./data/train", full.names=TRUE, pattern="dataframe-.*.csv.gz")
pal <- brewer.pal(8,"Dark2")
for ( i in 1:length(csv_files) ) {
    df=read.csv(csv_files[i], header=T)
    if (i<10) {
        name=sprintf("0%s", i)
    } else {
        name=sprintf("%s", i)
    }
    pic = sprintf("na_%s.jpg", name)
    print(pic)
    ndf=subset(df, df$naccess>5)
    jpeg(pic, width=480, height=480)
    wordcloud(ndf$dataset, ndf$naccess, max.words=100, rot.per=0, colors=pal, random.order=F, scale=c(4,1.), fixed.asp=T)
    dev.off()

    pic = sprintf("nu_%s.jpg", name)
    print(pic)
    ndf=subset(df, df$nusers>5)
    jpeg(pic, width=480, height=480)
    wordcloud(ndf$dataset, ndf$nusers, max.words=100, rot.per=0, colors=pal, random.order=F, scale=c(4,1.), fixed.asp=T)
    dev.off()

    pic = sprintf("cpu_%s.jpg", name)
    print(pic)
    ndf=subset(df, df$totcpu>5000)
    jpeg(pic, width=480, height=480)
    wordcloud(ndf$dataset, ndf$totcpu, max.words=100, rot.per=0, colors=pal, random.order=F, scale=c(4,1.), fixed.asp=T)
    dev.off()
}

# then convert all pic_XX.jpg into animated gif
cmd <- sprintf("convert -delay 30 -loop 0 na*.jpg naccess_cloud.gif")
system(cmd)
cmd <- sprintf("convert -delay 30 -loop 0 nu*.jpg nusers_cloud.gif")
system(cmd)
cmd <- sprintf("convert -delay 30 -loop 0 cpu*.jpg cpu_cloud.gif")
system(cmd)
cmd <- sprintf("rm na*.jpg nu*.jpg cpu*.jpg")
system(cmd)
