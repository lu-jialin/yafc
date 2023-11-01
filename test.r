library('plot.matrix')
source('pdg.r')

#pdg<-rbind(rep(0,ncol(pdg)),pdg)
#pdg<-cbind(rep(0,nrow(pdg)),pdg)

pdf('o/pdg.pdf')
plot(pdg,col=c('coral3','white','chartreuse4'),family='mono')
dev.off()
