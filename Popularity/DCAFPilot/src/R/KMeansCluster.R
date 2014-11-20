#!/usr/bin/env Rscript
# clean-up session parameters
#rm(list=ls())

# load libraries, helper functions, set seed.
source("R/helper.R")
require(graphics)
require(cluster)
require(fpc)

# helper function to create clusters
RunClusters<-function(x,NumCluster=2,printCluster=F){
  print(sprintf("Run Clustering with nc=%i", NumCluster))
  system("mkdir -p plots")
  system("rm plots/*.png")
  #Run cluster
  Cluster<-kmeans(x,NumCluster)
  #print Results
  if (printCluster) {
    print (Cluster)
  }
  #Plot Clusters
  # Make Plot Clusters
  fig.name <- paste0("plots/KMeansClusterOf",NumCluster,"nodesType1", ext)
  start.plot(fig.name)
  par(mfrow=c(1,1))
  plot(x,col=Cluster$cluster)
  #plot Centers
  points(Cluster$centers,col=1:2,pch=8)
  dev.off()
  #makePlot 2
  fig.name <- paste0("plots/KMeansClusterOf",NumCluster,"nodesType2", ext)
  start.plot(fig.name)
  par(mfrow=c(1,1))
  plotcluster(x,Cluster$cluster)
  dev.off()
  #makeplot 3
  fig.name <- paste0("plots/KMeansClusterOf",NumCluster,"nodesType3", ext)
  start.plot(fig.name)
  par(mfrow=c(1,1))
  clusplot(x,Cluster$cluster,color=TRUE,shade=TRUE,labels=2,lines=0)
  dev.off()
  return(Cluster)
}

do.clustering <- function(tdf, nc=seq(2:10)) {
    # exclude id columne to work with ML
    train.df <- drop(tdf, c("id", "PassengerId", "Survived"))
    # create new data frame and add clusters to it
    df <- data.frame(id=seq(1:nrow(tdf)))

    for(i in nc){
      cls <- RunClusters(train.df,i)
      df <- cbind(df, cls$cluster)
      df.names <- names(df)
      df.names[length(df.names)] <- sprintf("cls.%d", i)
      names(df) <- df.names
    }
    return(df)
}

# helper function to add cluster with given nc to given dataframe
add.cluster <- function(x, nc) {
    # exclude PassengerId/Survived while doing clustering, but save it for later
    pid <- x$PassengerId
    sur <- x$Survived
    d <- drop(x, c("id", "PassengerId", "Survived"))
    cls <- kmeans(d, nc)
    cname <- sprintf("cls.%i", nc)
    d[,c(cname)] <- cls$cluster
    # put back PassengerId/Survived
    d$PassengerId <- pid
    d$Survived <- sur
    return (d)
}

test.clustering <- function(traindata, testdata, nclusters=c(7)) {
    # re-run ML with additional cluster info
    print(sprintf("### Run Clustering ###"))
    set.seed(1)
    for(nc in nclusters) {
        fname <- sprintf("rf%i", nc)
        cat("\n--------------------------\n")
        print(sprintf("Add cluster %d", nc))
        train.dd <- add.cluster(traindata, nc)
        test.dd <- add.cluster(testdata, nc)
        do.ksvm(train.dd, test.dd, fname)
        do.rf(train.dd, test.dd, fname)
    }
}
