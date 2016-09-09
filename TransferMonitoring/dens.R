#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

# load data
my.path <- paste0(getwd(), "/")
# example
# load.data <- read.csv(paste0(my.path, file.name), header=TRUE)

# set seed
set.seed(12345)

fname = sprintf('phedextransfer.txt')
fname = sprintf('preds.csv')
df=read.csv(fname, header=F)
names(df)=c("real", "pred")
print(sprintf("Summary: df$real"))
print(summary(df$real))
print(sprintf("Summary: df$pred"))
dist=(df$real-df$pred)
print(sprintf("Mean %s", mean(dist)))
print(sprintf("Median %s", median(dist)))
print(sprintf("SD %s", sd(dist)))
print(summary(df$pred))
RMSE = sqrt(mean((df$real-df$pred)^2))
print(sprintf("RMSE df %s", RMSE))

print("Take subset of transfers with tf<1000")
ndf = subset(df, df$real<1000)

dist=(ndf$real-ndf$pred)
print(sprintf("Summary: ndf$real"))
print(summary(ndf$real))
print(sprintf("Summary: ndf$pred"))
print(summary(ndf$pred))
print(sprintf("Summary: dist"))
print(summary(dist))
print(sprintf("Mean %s", mean(dist)))
print(sprintf("Median %s", median(dist)))
print(sprintf("SD %s", sd(dist)))
RMSE = sqrt(mean((ndf$real-ndf$pred)^2))
print(sprintf("RMSE ndf %s", RMSE))

# cut-off value
mv=500

# make density plot
pdf("dens.pdf")
hist(dist, freq=F, xlab="(real-pred)/real", main="Distribution of Phedex Transfers", col="lightgreen", xlim=c(-mv,mv))
curve(dnorm(x, mean=mean(dist), sd=sd(dist)), add=TRUE, col="darkblue", lwd=2)
dev.off()
