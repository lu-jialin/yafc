#!/bin/env Rscript
#nnoremap gx :w<CR>:!Rscript test.r && mupdf o/pdg.pdf<CR>
library('plot.matrix')
source('pdg.r')

theme = list()
theme[['greenred']] = c('coral3','white','chartreuse4')

pdf('o/pdg.pdf')
par(mar=diag(diag(4)*4))
plot(pdg,col=theme$greenred,family='mono')
dev.off()
