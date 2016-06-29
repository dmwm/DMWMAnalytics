library(reshape2)
library(ggplot2)

names <- list.files(path = "C:/Users/Kipras Kancys/Desktop/CERN/Data/")
path = c()
path[1] <- paste0("C:/Users/Kipras Kancys/Desktop/CERN/Data/", names[1]) 
path[2] <- paste0("C:/Users/Kipras Kancys/Desktop/CERN/Data/", names[2]) 

data1 <- read.csv(path[1])
data2 <- read.csv(path[2])

both <- intersect(colnames(data1), colnames(data2))

data1 <- data1[, which(colnames(data1) %in% both)]
data2 <- data2[, which(colnames(data2) %in% both)]

pdf("plots.pdf", onefile = TRUE)

for (i in seq(1, ncol(data1), by = 2 )){
    
    d1 <- melt(data1[, i:(i+1)])
    d2 <- melt(data2[, i:(i+1)])
    
    d1$week <- "Before the bug"
    d2$week <- "After the bug"
    
    
    data <- rbind(d1, d2)
    
    data$week <- factor(data$week, levels = c("Before the bug", "After the bug"))

    gp <- ggplot(data, aes(x = value)) + 
        facet_wrap(c("variable","week"), scales = "free_x") +
        geom_histogram()
    
    print(gp)
    
}
dev.off()
     
    