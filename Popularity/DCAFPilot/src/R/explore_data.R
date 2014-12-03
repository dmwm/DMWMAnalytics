#!/usr/bin/env Rscript
# clean-up session parameters
rm(list=ls())

library(corrplot)
library(ggplot2)

# load data
my.path <- "/Users/vk/CMS/DMWM/GIT/CMS-DMWM-Analytics-data/Popularity/DCAFPilot/data/0.0.2/"

# set seed
set.seed(12345)

df1 = read.csv(paste0(my.path, "dataframe-20140101-20140108.csv.gz"), header=T)
df2 = read.csv(paste0(my.path, "dataframe-20140108-20140115.csv.gz"), header=T)
df3 = read.csv(paste0(my.path, "dataframe-20140115-20140122.csv.gz"), header=T)
df4 = read.csv(paste0(my.path, "dataframe-20140122-20140129.csv.gz"), header=T)
df5 = read.csv(paste0(my.path, "dataframe-20140129-20140205.csv.gz"), header=T)
df6 = read.csv(paste0(my.path, "dataframe-20140205-20140212.csv.gz"), header=T)
df7 = read.csv(paste0(my.path, "dataframe-20140212-20140219.csv.gz"), header=T)
df8 = read.csv(paste0(my.path, "dataframe-20140219-20140226.csv.gz"), header=T)
df9 = read.csv(paste0(my.path, "dataframe-20140226-20140305.csv.gz"), header=T)
df10 = read.csv(paste0(my.path, "dataframe-20140305-20140312.csv.gz"), header=T)
df11 = read.csv(paste0(my.path, "dataframe-20140312-20140319.csv.gz"), header=T)
df12 = read.csv(paste0(my.path, "dataframe-20140319-20140326.csv.gz"), header=T)
df13 = read.csv(paste0(my.path, "dataframe-20140326-20140402.csv.gz"), header=T)
df14 = read.csv(paste0(my.path, "dataframe-20140402-20140409.csv.gz"), header=T)
df15 = read.csv(paste0(my.path, "dataframe-20140409-20140416.csv.gz"), header=T)
df16 = read.csv(paste0(my.path, "dataframe-20140416-20140423.csv.gz"), header=T)
df17 = read.csv(paste0(my.path, "dataframe-20140423-20140430.csv.gz"), header=T)
df18 = read.csv(paste0(my.path, "dataframe-20140430-20140507.csv.gz"), header=T)
df19 = read.csv(paste0(my.path, "dataframe-20140507-20140514.csv.gz"), header=T)
df20 = read.csv(paste0(my.path, "dataframe-20140514-20140521.csv.gz"), header=T)
df21 = read.csv(paste0(my.path, "dataframe-20140521-20140528.csv.gz"), header=T)
df22 = read.csv(paste0(my.path, "dataframe-20140528-20140604.csv.gz"), header=T)
df23 = read.csv(paste0(my.path, "dataframe-20140604-20140611.csv.gz"), header=T)
df24 = read.csv(paste0(my.path, "dataframe-20140611-20140618.csv.gz"), header=T)
df25 = read.csv(paste0(my.path, "dataframe-20140618-20140625.csv.gz"), header=T)
df26 = read.csv(paste0(my.path, "dataframe-20140625-20140702.csv.gz"), header=T)
df27 = read.csv(paste0(my.path, "dataframe-20140702-20140709.csv.gz"), header=T)
df28 = read.csv(paste0(my.path, "dataframe-20140709-20140716.csv.gz"), header=T)
df29 = read.csv(paste0(my.path, "dataframe-20140716-20140723.csv.gz"), header=T)
df30 = read.csv(paste0(my.path, "dataframe-20140723-20140730.csv.gz"), header=T)
df31 = read.csv(paste0(my.path, "dataframe-20140730-20140806.csv.gz"), header=T)
df32 = read.csv(paste0(my.path, "dataframe-20140806-20140813.csv.gz"), header=T)
df33 = read.csv(paste0(my.path, "dataframe-20140813-20140820.csv.gz"), header=T)
df34 = read.csv(paste0(my.path, "dataframe-20140820-20140827.csv.gz"), header=T)
df35 = read.csv(paste0(my.path, "dataframe-20140827-20140903.csv.gz"), header=T)
df36 = read.csv(paste0(my.path, "dataframe-20140903-20140910.csv.gz"), header=T)
df37 = read.csv(paste0(my.path, "dataframe-20140910-20140917.csv.gz"), header=T)
df38 = read.csv(paste0(my.path, "dataframe-20140917-20140924.csv.gz"), header=T)
df39 = read.csv(paste0(my.path, "dataframe-20140924-20141001.csv.gz"), header=T)
df40 = read.csv(paste0(my.path, "dataframe-20141001-20141008.csv.gz"), header=T)
df41 = read.csv(paste0(my.path, "dataframe-20141008-20141015.csv.gz"), header=T)
df42 = read.csv(paste0(my.path, "dataframe-20141015-20141022.csv.gz"), header=T)
df43 = read.csv(paste0(my.path, "dataframe-20141022-20141029.csv.gz"), header=T)
df44 = read.csv(paste0(my.path, "dataframe-20141029-20141105.csv.gz"), header=T)
df45 = read.csv(paste0(my.path, "dataframe-20141105-20141112.csv.gz"), header=T)
df46 = read.csv(paste0(my.path, "dataframe-20141112-20141119.csv.gz"), header=T)
df47 = read.csv(paste0(my.path, "dataframe-20141119-20141126.csv.gz"), header=T)

pdf("data1.pdf")
par(mfrow=c(2,2))
hist(df1$dbs, main="DBS instance")
hist(df1$era, main="DBS era")
hist(df1$primds, main="DBS primary dataset")
hist(df1$tier, main="DBS tier")
dev.off()

pdf("data2.pdf")
par(mfrow=c(2,2))
hist(log(df1$nevt), main="Number of events in dataset (log)")
hist(log(df1$nlumis), main="Number of lumis in dataset (log)")
hist(log(df1$nfiles), main="Number of files in dataset (log)")
hist(log(df1$nblk), main="Number of blocks in dataset (log)")
dev.off()

pdf("data3.pdf")
par(mfrow=c(2,2))
hist(log(df1$nsites), main="Number of sites (log)")
hist(log(df1$proc_evts), main="Number of processed events (log)")
hist(log(df1$cpu), main="CPU")
hist(log(df1$wct), main="Wall clock time")
dev.off()

# combine all dataframes into single list
frames=list(df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14, df15, df16, df17, df18, df19, df20, df21, df22, df23, df24, df25, df26, df27, df28, df29, df30, df31, df32, df33, df34, df35, df36, df37, df38, df39, df40, df41, df41, df42, df43, df44, df45, df46, df47)

# make animated gifs

# dbs.gif shows DBS instance usage movement
for(idx in 1:length(frames)) { name=paste0(idx, ".jpg"); if(idx<10) name=paste0("0",name); jpeg(name); hist(frames[[idx]]$dbs, main="DBS usage"); dev.off() }
cmd <- sprintf("convert -delay 100 -loop 0 *.jpg dbs.gif")
system(cmd)

# DBS plots 1
for(idx in 1:length(frames)) {
    name=paste0(idx, ".jpg"); if(idx<10) name=paste0("0",name);
    df <- subset(frames[[idx]], frames[[idx]]$target>0)
    jpeg(name);
    par(mfrow=c(2,2))
    hist(df$dbs, main="DBS instance", xlab="dbs isntances", col="red", ylim=c(0,250))
    hist(df$era, main="DBS era", xlab="era", col="blue", ylim=c(0,250))
    hist(df$primds, main="DBS primary dataset", xlab="primds", col="green", ylim=c(0,100))
    hist(df$tier, main="DBS tier", xlab="tier", xlim=c(0,25), col="yellow", ylim=c(0,150))
    dev.off()
}
cmd <- sprintf("convert -delay 100 -loop 0 *.jpg dbs1.gif")
system(cmd)

# DBS plots 2
for(idx in 1:length(frames)) {
    name=paste0(idx, ".jpg"); if(idx<10) name=paste0("0",name);
    df <- subset(frames[[idx]], frames[[idx]]$target>0)
    jpeg(name);
    par(mfrow=c(2,2))
    hist(log(df$nevt), main="Number of events in dataset (log)", xlab="nevt", xlim=c(0,25), col="red", ylim=c(0,100))
    hist(log(df$nlumis), main="Number of lumis in dataset (log)", xlab="nlumis", xlim=c(0,15), col="blue", ylim=c(0,180))
    hist(log(df$nfiles), main="Number of files in dataset (log)", xlab="nfiles", xlim=c(0,15), col="green", ylim=c(0,150))
    hist(log(df$nblk), main="Number of blocks in dataset (log)", xlab="nblk", xlim=c(0,10), col="yellow", ylim=c(0,150))
    dev.off()
}
cmd <- sprintf("convert -delay 100 -loop 0 *.jpg dbs2.gif")
system(cmd)

# DBS plots 3
for(idx in 1:length(frames)) {
    name=paste0(idx, ".jpg"); if(idx<10) name=paste0("0",name);
    df <- subset(frames[[idx]], frames[[idx]]$target>0)
    jpeg(name);
    par(mfrow=c(2,2))
    hist(log(df$nsites), main="Number of sites (log)", xlab="# sites", col="red", ylim=c(0,100))
    hist(log(df$proc_evts), main="Number of processed events (log)", xlab="Processing events", xlim=c(0,25), col="blue", ylim=c(0,120))
    hist(log(df$cpu), main="CPU", xlab="CPU usage", xlim=c(0,20), col="green", ylim=c(0,100))
    hist(log(df$wct), main="Wall clock time", xlab="wct", xlim=c(0,25), col="yellow", ylim=c(0,100))
    dev.off()
}
cmd <- sprintf("convert -delay 100 -loop 0 *.jpg dbs3.gif")
system(cmd)

# Correlations
# helper function to drop columns from given dataset
drop <- function(xdf, drops) {
    return(xdf[,!names(xdf) %in% drops])
}
keep <- function(xdf, keeps) {
    return(xdf[,names(xdf) %in% keeps])
}
keeps <- c("creator", "dataset", "dbs", "dtype", "era", "nblk", "nevt", "nfiles", "nlumis", "nrel", "nsites", "parent", "primds", "proc_evts", "procds", "size", "cpu", "wct", "tier")
for(idx in 1:length(frames)) {
    name=paste0(idx, ".jpg"); if(idx<10) name=paste0("0",name);
#    df <- drop(frames[[idx]], c("id", "target"))
    df <- subset(frames[[idx]], frames[[idx]]$target>0)
    df <- keep(df, keeps)
    # make correlation matrix
    jdx <- 2
    cor.matrix <- cor(df[,jdx:ncol(df)])
    colnames(cor.matrix) <- names(df)[jdx:ncol(df)]
    rownames(cor.matrix) <- names(df)[jdx:ncol(df)]
    correlations <- as.numeric(cor.matrix)
    # round to 2 digits correlation matrix and plot it
    cor <- round(cor.matrix, digits=2)
    jpeg(name);
    corrplot(cor, method="circle", shade.col=NA, tl.col="black", tl.srt=45, bg="transparent")
    dev.off()
}
cmd <- sprintf("convert -delay 100 -loop 0 *.jpg corr.gif")
system(cmd)

# get some dataset flow
datasets=head(df1[with(df1, order(-target)), c("dataset")])
make.dd <- function(d) {dd=data.frame(did=d); for(idx in 1:length(frames)) {name=sprintf("v%d",idx); v=subset(frames[[idx]], frames[[idx]]$dataset==d)$target; dd[,name]=v}; return(dd)}
sdf=data.frame()
for(dataset in datasets) {sdf=rbind(sdf,make.dd(dataset)); sdf[is.na(sdf)] <- 0}

jpeg("popularity.jpg")
plot(s, sdf[1,seq(2,48)], type="l", xlab="weeks", ylab="popularity", col="black", ylim=c(0,0.3), lwd=2)
par(new=T)
plot(s, sdf[2,seq(2,48)], type="l", xlab="weeks", ylab="popularity", col="blue", ylim=c(0,0.3), lwd=2)
par(new=T)
plot(s, sdf[3,seq(2,48)], type="l", xlab="weeks", ylab="popularity", col="green", ylim=c(0,0.3), lwd=2)
par(new=T)
plot(s, sdf[4,seq(2,48)], type="l", xlab="weeks", ylab="popularity", col="red", ylim=c(0,0.3), lwd=2)
par(new=T)
plot(s, sdf[5,seq(2,48)], type="l", xlab="weeks", ylab="popularity", col="magenta", ylim=c(0,0.3), lwd=2)
dev.off()

