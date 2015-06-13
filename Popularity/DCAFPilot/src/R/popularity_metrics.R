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
libs <- c("corrplot", "ggplot2", "data.table", "plyr", "dplyr")
for(i in 1:length(libs)) {
    pkg <- sprintf("%s", libs[i])
    print(sprintf("load %s", pkg))
    suppressMessages(library(pkg, character.only = TRUE))
}

df13=read.csv('2014.csv.gz', header=T)
df14=read.csv('2014.csv.gz', header=T)
df15=read.csv('2015.csv.gz', header=T)
ndf13=subset(df13, df13$naccess!=0)
ndf14=subset(df14, df14$naccess!=0)
ndf15=subset(df15, df15$naccess!=0)
col1=rgb(1,0,0,0.5)
col2=rgb(0,0,1,0.5)
col3=rgb(0,1,0,0.5)

# naccess plot
pdf(sprintf("naccess.pdf"))
hist(log(ndf13$naccess), freq=F, col=col1,xlim=c(0,15), ylim=c(0,0.2), xlab="Number of accesses, log scale", main="")
hist(log(ndf14$naccess), freq=F, col=col2, add=T)
hist(log(ndf15$naccess), freq=F, col=col3, add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10)
dev.off()

# totcpu plot
pdf(sprintf("totcpu.pdf"))
hist(log(ndf13$totcpu),freq=F,col=col1,xlim=c(0,15),xlab="total CPU hours, log scale", main="",ylim=c(0,0.2))
hist(log(ndf14$totcpu),freq=F,col=col2,xlim=c(0,15),add=T)
hist(log(ndf15$totcpu),freq=F,col=col3,xlim=c(0,15),add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10)> dev.off()

# nusers*days plot
pdf(sprintf("nusers.pdf"))
hist(log(ndf13$nuser), freq=F, col=col1,xlim=c(0,5),xlab="Number of users*day, log scale", main="", ylim=c(0,3))
hist(log(ndf14$nuser), freq=F, col=col2,xlim=c(0,5),add=T)
hist(log(ndf15$nuser), freq=F, col=col3,xlim=c(0,5),add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10)
dev.off()
