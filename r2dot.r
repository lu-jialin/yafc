#!/bin/env Rscript
#nnoremap gx :w<CR>:!Rscript <C-R>% #&& mupdf o/pdg.pdf<CR>
rm()
source(commandArgs(trailingOnly=TRUE)[1])
#source('pdg.r')
#TODO : Dynamic bind `pdg name via `ninja

tvltvl<-1
#Set `tvltvl` to a large number to show that which was set
tvl <- colSums(pdg!=0)==0 #Without loop back end node here
#diag(pdg[tvl,tvl]) = tvltvl
diag(pdg[c(FALSE,tvl[1:(length(tvl)-1)]),tvl]) <- tvltvl
pdg[ncol(pdg),ncol(pdg)] <- 0
pdg_insign <- c('[start]',as.list(pdg_insign),'[end]')
#Use `as.list` to avoid charter==c(charter) in R
pdg_input <- c(NA,as.list(pdg_input),NA)
pdg_output <- c(NA,as.list(pdg_output),NA)
pdg_input  [[length(pdg_insign)+1]] <- NA ; pdg_input  <- pdg_input  [1:length(pdg_insign)] ; pdg_input [sapply( pdg_input ,is.null)] <- NA
pdg_output [[length(pdg_insign)+1]] <- NA ; pdg_output <- pdg_output [1:length(pdg_insign)] ; pdg_output [sapply( pdg_output ,is.null)] <- NA
#NULL cannot keep the none-IO head. Note that `is.null` is NOT vectorization
#NOTE : A COMPLETE std-matrix here
#pdg[,rowSums(pdg!=0)==0] #Start of#The start point
#pdg[,colSums(pdg!=0)==0] #Start of#The end point
#pdg[,colSums(pdg!=0)==2] #Start of#Branchs(loop or if)
#pdg[,colSums(pdg!=0)==1] #Start of#Atoms(IO or trival)
##Extrange col and row can get #end of#

############################################
dot=cat ; dotdebug=function(...){invisible()}
#dot=function(...){invisible()} ; dotdebug=print #debug

dot('digraph"','pdg','"{rankdir=TD ',sep='')
dot('graph[fontname="CMU Typewriter Text"]',sep='')
dot('node[fontname="CMU Typewriter Text"]',sep='')
dot('edge[fontname="CMU Typewriter Text"arrowhead=vee arrowtail=vee]',sep='')
#! : `rankdir` will exchange the coordinate-order and x-grid y-grid methods
#Currently is column-major, aka (y,x)

#Style grid before the actual nodes
coor <- diag(ncol(pdg))
coor <- as.data.frame(coor)

for(i in 1:nrow(coor)) for(j in 1:ncol(coor)) coor[i,j] <- paste0('"',i,' ',j,'"')
dot(as.character(sapply(coor,function(c)paste0(c,'[label="" shape=none width=0 height=0]'))),sep='')
#dot(as.character(sapply(coor,function(c)paste0(c,'[shape=box]'))),sep='')

#x grid
showgrid <- 'invis'
grid <- 1:length(coor)
grid <- rbind(grid,matrix(0,length(coor)-1,length(coor)))
#e_ <- diag(rep(0,length(coor))) ; e_[,1] <- 1 ; grid <- e_ %*% grid
e_ <- diag(diag(length(coor))) ; grid <- t(e_ %*% grid) %*% e_
#``data.fram as V-V-matrix``
grid <- as.data.frame(grid)
#grid <- c(grid)
for(i in 1:length(grid))grid[i]<-lapply(grid[i],function(col)paste0('"',i,' ',col,'"'))
grid <- as.data.frame(grid)
grid[1:(length(grid)-1),] <- lapply(grid[1:(length(grid)-1),],function(n)paste0(n,'->'))
#diag(grid) <- ''
for(col in grid)dot(paste0(c('{rank=same edge[dir=none style=',showgrid,']',col,'}')),sep='')

#y grid
grid <- 1:length(coor)
grid <- rbind(grid,matrix(0,length(coor)-1,length(coor)))
#e_ <- diag(rep(0,length(coor))) ; e_[,1] <- 1 ; grid <- e_ %*% grid
e_ <- diag(diag(length(coor))) ; grid <- t(e_ %*% grid) %*% e_
#``data.fram as V-V-matrix``
grid <- as.data.frame(grid)
#grid <- c(grid)
for(i in 1:length(grid))grid[i]<-lapply(grid[i],function(col)paste0('"',i,' ',col,'"'))
grid <- as.data.frame(grid)
grid[,1:(length(grid)-1)] <- lapply(grid[,1:(length(grid)-1)],function(n)paste0(n,'->'))
#diag(grid) <- ''
grid<-t(grid)
dot('{edge[dir=none style=',showgrid,']',sep='') ; for(col in grid)dot(paste0(col),sep='') ; dot('}',sep='')

pdg_insign[rowSums(pdg!=0)==0] <- sapply(pdg_insign[rowSums(pdg!=0)==0],function(step)paste0('[label="',step,'" shape=circle]'))

pdg_insign[colSums(pdg!=0)==2] <- sapply(pdg_insign[colSums(pdg!=0)==2],function(step)paste0('[label="',step,'" shape=diamond]'))
pdg_insign[!is.na(pdg_output)] <- sapply(pdg_insign[!is.na(pdg_output)],function(step)paste0('[label="',step,'" shape=parallelogram]'))
pdg_insign[is.na(pdg_output)&colSums(pdg!=0)==1&rowSums(pdg!=0)!=0] <- as.vector(sapply(pdg_insign[is.na(pdg_output)&colSums(pdg!=0)==1&rowSums(pdg!=0)!=0],function(step)paste0('[label="',step,'" shape=box]')))

pdg_insign[colSums(pdg!=0)==0] <- sapply(pdg_insign[colSums(pdg!=0)==0],function(step)paste0('[label="',step,'" shape=circle]'))

#TODO : Refer to ``data.fram as V-V-matrix``
for(i in 1:length(pdg_insign))pdg_insign[[i]] <- paste0('"',i,' ',i,'"',pdg_insign[[i]])
dot(as.character(paste0(pdg_insign)))

false <- which(pdg==-1,arr.ind=TRUE)
false <- as.data.frame(matrix(c(t(false)),nrow=2))
dot('{edge[label="/F"]',sep='')
dot(as.character(lapply(false,function(yx)paste0('"',yx[2],' ',yx[2],'"','->','"',yx[1],' ',yx[1],'"'))),sep='')
dot('}',sep='')

true <- which(pdg==1,arr.ind=TRUE)
true <- as.data.frame(matrix(c(t(true)),nrow=2))
dot('{edge[label="/T"]',sep='')
dot(as.character(lapply(true,function(yx)paste0('"',yx[2],' ',yx[2],'"','->','"',yx[1],' ',yx[1],'"'))),sep='')
dot('}',sep='')

dot(sapply(which(!is.na(pdg_output)) , function(n){
	paste0('{rank=same',
	paste0('{"',n,' i"[label=""shape=none width=0 height=0]}->','"',n,' ',n,'"[label="',pdg_input[n],'"style=dashed]') ,
	paste0('"',n,' ',n,'"->','{"',n,' o"[label=""shape=none width=0 height=0]}','[label="',pdg_output[n],'"style=dashed]') ,
	'}')
}))

#library(xtable);dotdebug(xtable(coor,digits=0))

dot('}',sep='')
