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
df13=subset(df13, df13$naccess!=0)
df14=subset(df14, df14$naccess!=0)
df15=subset(df15, df15$naccess!=0)
col1=rgb(1,0,0,0.5)
col2=rgb(0,0,1,0.5)
col3=rgb(0,1,0,0.5)

# naccess plot
pdf(sprintf("naccess_norm.pdf"))
h1=hist(log10(df13$naccess/nrow(df13)), plot=F)
h2=hist(log10(df14$naccess/nrow(df14)), plot=F)
h3=hist(log10(df15$naccess/nrow(df15)), plot=F)
h1$counts = log10(h1$counts)
h2$counts = log10(h2$counts)
h3$counts = log10(h3$counts)
plot(h1, ylab="log10(Frequency)", xlab="log10(naccess)", ylim=c(0,6), col=col1, main="", font.axis=2, cex.lab=1.2, ps=14)
plot(h2, col=col2, add=T)
plot(h3, col=col3, add=T)
#hist(log10(df13$naccess), freq=F, col=col1,xlim=c(0,15), xlab="Number of accesses, log10 scale", main="")
#hist(log10(df14$naccess), freq=F, col=col2, add=T)
#hist(log10(df15$naccess), freq=F, col=col3, add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10, text.font=2)
dev.off()

print("naccess")
print(h1$breaks)
print(h1)
# print(h1$counts)
# print(h2$breaks)
# print(h2$counts)
# print(h3$breaks)
# print(h3$counts)
y1=c(h1$counts, 0)
y2=c(h2$counts, 0)
y3=c(0,h3$counts)
# xrange=seq(-5,2,0.5)
xrange=seq(0,7,0.5)
pdf(sprintf("naccess_stack.pdf"))
barplot(rbind(y1,y2,y3),col=c(col1,col2,col3),names.arg=xrange[-1],space=0,las=1,ylab="log10(Frequency)", xlab="log10(naccess)")
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10, text.font=2)
dev.off()

pdf(sprintf("naccess_lines.pdf"))
print("xrange")
print(length(xrange))
print(length(y1))
print(length(y2))
print(length(y3))
plot(xrange[-1], y1, type="l", ylab="log10(Frequency)", xlab="log10(naccess)", col=col1, main="", font.axis=2, cex.lab=1.2, ps=14, lwd=3)
lines(xrange[-1], y2, type="l", col=col2, lwd=3)
lines(xrange[-1], y3, type="l", col=col3, lwd=3)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10, text.font=2)
dev.off()

# totcpu plot
pdf(sprintf("totcpu_norm.pdf"))
h1=hist(log10(df13$totcpu/nrow(df13)), plot=F)
h2=hist(log10(df14$totcpu/nrow(df14)), plot=F)
h3=hist(log10(df15$totcpu/nrow(df15)), plot=F)
h1$counts = log10(h1$counts)
h2$counts = log10(h2$counts)
h3$counts = log10(h3$counts)
plot(h1, ylab="log10(Frequency)", xlab="log10(totcpu)", ylim=c(0,6), col=col1, main="", font.axis=2, cex.lab=1.2, ps=14)
plot(h2, col=col2, add=T)
plot(h3, col=col3, add=T)
#hist(log10(df13$totcpu),freq=F,col=col1,xlim=c(0,15),xlab="total CPU hours, log10 scale", main="", ylim=c(0,3))
#hist(log10(df14$totcpu),freq=F,col=col2,xlim=c(0,15),add=T)
#hist(log10(df15$totcpu),freq=F,col=col3,xlim=c(0,15),add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10, text.font=2)
dev.off()

print("totcpu")
print(h1)
# print(h1$breaks)
# print(h1$counts)
# print(h2$breaks)
# print(h2$counts)
# print(h3$breaks)
# print(h3$counts)
y1=c(h1$counts, 0)
y2=c(h2$counts, 0)
y3=c(0,h3$counts)
# xrange=seq(-5,1.5,0.5)
xrange=seq(0,6.5,0.5)
pdf(sprintf("totcpu_stack.pdf"))
barplot(rbind(y1,y2,y3),col=c(col1,col2,col3),names.arg=xrange[-1],space=0,las=1,ylab="log10(Frequency)", xlab="log10(totcpu)")
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10, text.font=2)
dev.off()

pdf(sprintf("totcpu_lines.pdf"))
plot(xrange[-1], y1, type="l", ylab="log10(Frequency)", xlab="log10(totcpu)", col=col1, main="", font.axis=2, cex.lab=1.2, ps=14, lwd=3)
lines(xrange[-1], y2, type="l", col=col2, lwd=3)
lines(xrange[-1], y3, type="l", col=col3, lwd=3)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10, text.font=2)
dev.off()

# nusers*days plot
pdf(sprintf("nusers_norm.pdf"))
h1=hist(log10(df13$nuser/nrow(df13)), plot=F)
h2=hist(log10(df14$nuser/nrow(df14)), plot=F)
h3=hist(log10(df15$nuser/nrow(df15)), plot=F)
h1$counts = log10(h1$counts)
h2$counts = log10(h2$counts)
h3$counts = log10(h3$counts)
plot(h1, ylab="log10(Frequency)", xlab="log10(nuser)", ylim=c(0,6), col=col1, main="", font.axis=2, cex.lab=1.2, ps=14)
plot(h2, col=col2, add=T)
plot(h3, col=col3, add=T)
#hist(log10(df13$nuser), freq=F, col=col1,xlim=c(0,5),xlab="Number of users*day, log10 scale", main="")
#hist(log10(df14$nuser), freq=F, col=col2,xlim=c(0,5),add=T)
#hist(log10(df15$nuser), freq=F, col=col3,xlim=c(0,5),add=T)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10, text.font=2)
dev.off()

print("nusers")
print(h1)
# print(h1$breaks)
# print(h1$counts)
# print(h2$breaks)
# print(h2$counts)
# print(h3$breaks)
# print(h3$counts)

y1=c(h1$counts, 0)
y2=c(0, h2$counts, 0,0,0)
y3=c(0,0,0,0,0,0,h3$counts)
y1[is.infinite(y1)]=0
y2[is.infinite(y2)]=0
y3[is.infinite(y3)]=0
# xrange=seq(-5,-2.6,0.1)
xrange=seq(0,2.4,0.1)
pdf(sprintf("nusers_stack.pdf"))
barplot(rbind(y1,y2,y3),col=c(col1,col2,col3),names.arg=xrange[-1],space=0,las=1,ylab="log10(Frequency)", xlab="log10(nuser)")
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10, text.font=2)
dev.off()

pdf(sprintf("nusers_lines.pdf"))
plot(xrange[-1], y1, type="l", ylab="log10(Frequency)", xlab="log10(nusers)", col=col1, main="", font.axis=2, cex.lab=1.2, ps=14, lwd=3)
lines(xrange[-1], y2, type="l", col=col2, lwd=3)
lines(xrange[-1], y3, type="l", col=col3, lwd=3)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1, col2, col3), lwd=10, text.font=2)
dev.off()

pdf(sprintf("nusers_stack_short.pdf"))
start=12
xrange=xrange[start:length(xrange)]
y1=y1[start:length(y1)]
y2=y2[start:length(y2)]
y3=y3[12:length(y3)]
barplot(rbind(y1,y2,y3),col=c(col1,col2,col3),names.arg=xrange[-1],space=0,las=1)
legend("topright", c("2013 data", "2014 data", "2015 data"), col=c(col1,col2,col3), lwd=10, text.font=2)
dev.off()
