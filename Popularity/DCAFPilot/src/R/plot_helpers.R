# Plot Helper functions

# use PDF for high-quality plots, while png for rmd
ext <- ".pdf"
#ext <- ".png"

# helper function to initialize plotting function depending on file extention
start.plot <- function(f) {
    if (grepl("png$", f))
        png(f, bg="transparent")
    else if (grepl("pdf$", f))
        pdf(f)
    else if (grepl("jpg$", f))
        jpeg(f)
}

# helper functino to reset plot layout
graph.reset <- function() {
    par(mfrow=c(1,1))
#    dev.off()
}

# make correlation plot
make.cor.plot <- function (x, fname="cor", drops=NULL) {
    # drop requested attributes
    if(!is.null(drops))
        x <- drop(x, drops)

    df <- drop(x, c("id", "target"))
    # make correlation matrix
    idx <- 2
    cor.matrix <- cor(df[,idx:ncol(df)])
    colnames(cor.matrix) <- names(df)[idx:ncol(df)]
    rownames(cor.matrix) <- names(df)[idx:ncol(df)]
    correlations <- as.numeric(cor.matrix)

    # round to 2 digits correlation matrix and plot it
    fig.name <- paste0(fname, ext)
    print(sprintf("Make correlation plot %s", fig.name))
    start.plot(fig.name)
    cor <- round(cor.matrix, digits=2)
    corrplot(cor, method="shade", shade.col=NA, tl.col="black", tl.srt=45, addCoef.col="black", bg="transparent")
    dev.off()
    cat("====== Correlations ======\n")
    print(cor)
}

