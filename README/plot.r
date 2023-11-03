#!/bin/env Rscript
library('plot.matrix')
pdg <- readRDS(commandArgs(trailingOnly=TRUE)[1])
pdg <- pdg$M

theme = list()
theme[['greenred']] = c('coral3','white','chartreuse4')

#pdg<-rbind(rep(0,ncol(pdg)),pdg)
#pdg<-cbind(rep(0,nrow(pdg)),pdg)

pdf('o/pdg.pdf')
plot(pdg,col=c('coral3','white','chartreuse4'),family='mono')
par(mar=diag(diag(4)*4))
plot(pdg,col=theme$greenred,family='mono')
dev.off()
