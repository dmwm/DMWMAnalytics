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

df13=read.csv('data/2013.csv.gz', header=T)
df14=read.csv('data/2014.csv.gz', header=T)
df15=read.csv('data/2015.csv.gz', header=T)
#ndf13=subset(df13, df13$naccess!=0)
#ndf14=subset(df14, df14$naccess!=0)
#ndf15=subset(df15, df15$naccess!=0)

#939483,AOD
#772735,AODSIM
#193739,MINIAOD
#777543,MINIAODSIM
#305515,USER
tiers=c(939483,772735,193739,777543,305515)
ndf13=subset(df13, df13$tier%in%tiers)
ndf14=subset(df14, df14$tier%in%tiers)
ndf15=subset(df15, df15$tier%in%tiers)

#ndf13=subset(ndf13, ndf13$naccess!=0)
#ndf14=subset(ndf14, ndf14$naccess!=0)
#ndf15=subset(ndf15, ndf15$naccess!=0)

# apply a cut
ndf13=subset(ndf13, ndf13$naccess>10 && ndf13$totcpu>10)
ndf14=subset(ndf14, ndf14$naccess>10 && ndf15$totcpu>10)
ndf15=subset(ndf15, ndf15$naccess>10 && ndf15$totcpu>10)

# apply cut on nusers
#ndf13=subset(ndf13, log(ndf13$nuser)>2)
#ndf14=subset(ndf14, log(ndf14$nuser)>2)
#ndf15=subset(ndf15, log(ndf15$nuser)>2)

ntiers13 = nrow(subset(ndf13, ndf13$tier%in%tiers))
ntiers14 = nrow(subset(ndf14, ndf14$tier%in%tiers))
ntiers15 = nrow(subset(ndf15, ndf15$tier%in%tiers))
print(sprintf("Cut naccess>10 && totcpu>10, tiers13=%s, tiers14=%s, tiers15=%s", ntiers13, ntiers14, ntiers15))
ntiers13 = nrow(subset(df13, df13$tier%in%tiers))
ntiers14 = nrow(subset(df14, df14$tier%in%tiers))
ntiers15 = nrow(subset(df15, df15$tier%in%tiers))
print(sprintf("No cut, tiers13=%s, tiers14=%s, tiers15=%s", ntiers13, ntiers14, ntiers15))

print(nrow(ndf13))
print(nrow(ndf14))
print(nrow(ndf15))

col1=rgb(1,0,0,0.5)
col2=rgb(0,0,1,0.5)
col3=rgb(0,1,0,0.5)

# naccess plot
pdf(sprintf("naccess.pdf"))
cut=c(0,0.2)
cut=c(0,0.5)
hist(log(ndf13$naccess), freq=F, col=col1,xlim=c(0,15), ylim=cut, xlab="Number of accesses, log scale", main="")
hist(log(ndf14$naccess), freq=F, col=col2, add=T)
hist(log(ndf15$naccess), freq=F, col=col3, add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10)
dev.off()
print("done naccess.pdf")

# totcpu plot
pdf(sprintf("totcpu.pdf"))
cut=c(0,0.2)
cut=c(0,0.5)
hist(log(ndf13$totcpu),freq=F,col=col1,xlim=c(0,15),xlab="total CPU hours, log scale", main="",ylim=cut)
hist(log(ndf14$totcpu),freq=F,col=col2,xlim=c(0,15),add=T)
hist(log(ndf15$totcpu),freq=F,col=col3,xlim=c(0,15),add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10)
dev.off()
print("done totcpu.pdf")

# nusers*days plot
pdf(sprintf("nusers.pdf"))
hist(log(ndf13$nuser), freq=F, col=col1,xlim=c(0,5),xlab="Number of users*day, log scale", main="", ylim=c(0,3))
hist(log(ndf14$nuser), freq=F, col=col2,xlim=c(0,5),add=T)
hist(log(ndf15$nuser), freq=F, col=col3,xlim=c(0,5),add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10)
dev.off()
print("done nusers.pdf")
