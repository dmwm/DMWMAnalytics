#!/usr/bin/env Rscript
# author: V. Kuznetsov
# example taken from
# http://www.rstudio.com/ide/docs/r_markdown
# http://www.rstudio.com/ide/docs/authoring/using_markdown
# http://rprogramming.net/create-html-or-pdf-files-with-r-knitr-miktex-and-pandoc/
# Usage: rmd2htmlR --input=<file.Rmd>

cmd_args <- commandArgs();
#for (arg in cmd_args) cat("  ", arg, "\n", sep="");
file.rmd <- NA
for (arg in cmd_args) {
   match <- grep("\\.Rmd$", arg)
   if (length(match) == 1) {
      file.rmd = as.character(arg)
   }
}

if (is.na(file.rmd)) {
    cat("Usage: rmd2html.R <file.Rmd>\n")
    stop("No Rmd file is provided\n")
}

# create working area by using file base name and rmd2html extension
# all produced files will end-up over there
input.file <- file.rmd

pwd <- getwd()
file.rmd <- paste(pwd, file.rmd, sep="/")
file.dir <- gsub("Rmd$", "rmd2html", file.rmd)
cat("create", file.dir, "\n")
dir.create(file.dir, showWarnings = FALSE)
setwd(file.dir)

# generate appropriate file names
#file.html <- gsub("Rmd$", "html", file.rmd)
#file.md   <- gsub("Rmd$", "md", file.rmd)
#file.pdf  <- gsub("Rmd$", "pdf", file.rmd)
file.html <- paste(file.dir, gsub("Rmd$", "html", input.file), sep="/")
file.md <- paste(file.dir, gsub("Rmd$", "md", input.file), sep="/")
file.pdf <- paste(file.dir, gsub("Rmd$", "pdf", input.file), sep="/")
cat("process", file.rmd, file.html, file.md, file.pdf, "\n")

library(knitr)
library(markdown)
knit(file.rmd, output=file.md)
markdownToHTML(file.md, file.html, options=c("use_xhml"))

cmd <- paste(paste(paste("pandoc -s", file.html), "-o"), file.pdf)
cat("execute", cmd, "\n")
system(cmd)
