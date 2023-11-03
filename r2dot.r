#!/bin/env Rscript
#nnoremap gx :w<CR>:!Rscript <C-R>% #&& mupdf o/stdf$M.pdf<CR>
rm()
source(commandArgs(trailingOnly=TRUE)[1])
#source('stdf$M.r')
#TODO : Dynamic bind `stdf$M name via `ninja

tvltvl<-1
#Set `tvltvl` to a large number to show that which was set
tvl <- colSums(stdf$M!=0)==0 #Without loop back end node here
#diag(stdf$M[tvl,tvl]) = tvltvl
diag(stdf$M[c(FALSE,tvl[1:(length(tvl)-1)]),tvl]) <- tvltvl
stdf$M[ncol(stdf$M),ncol(stdf$M)] <- 0
stdf$I <- c('[start]',as.list(stdf$I),'[end]')
#Use `as.list` to avoid charter==c(charter) in R
stdf$i <- c(NA,as.list(stdf$i),NA)
stdf$o <- c(NA,as.list(stdf$o),NA)
stdf$i  [[length(stdf$I)+1]] <- NA ; stdf$i  <- stdf$i  [1:length(stdf$I)] ; stdf$i [sapply( stdf$i ,is.null)] <- NA
stdf$o [[length(stdf$I)+1]] <- NA ; stdf$o <- stdf$o [1:length(stdf$I)] ; stdf$o [sapply( stdf$o ,is.null)] <- NA
#NULL cannot keep the none-IO head. Note that `is.null` is NOT vectorization
#NOTE : A COMPLETE std-matrix here
#stdf$M[,rowSums(stdf$M!=0)==0] #Start of#The start point
#stdf$M[,colSums(stdf$M!=0)==0] #Start of#The end point
#stdf$M[,colSums(stdf$M!=0)==2] #Start of#Branchs(loop or if)
#stdf$M[,colSums(stdf$M!=0)==1] #Start of#Atoms(IO or trival)
##Extrange col and row can get #end of#

############################################
dot=cat ; dotdebug=function(...){invisible()}
#dot=function(...){invisible()} ; dotdebug=print #debug

dot('digraph"','stdf$M','"{rankdir=TD ',sep='')
dot('graph[fontname="CMU Typewriter Text"]',sep='')
dot('node[fontname="CMU Typewriter Text"]',sep='')
dot('edge[fontname="CMU Typewriter Text"arrowhead=vee arrowtail=vee]',sep='')
#! : `rankdir` will exchange the coordinate-order and x-grid y-grid methods
#Currently is column-major, aka (y,x)

#Style grid before the actual nodes
coor <- diag(ncol(stdf$M))
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

stdf$I[rowSums(stdf$M!=0)==0] <- sapply(stdf$I[rowSums(stdf$M!=0)==0],function(step)paste0('[label="',step,'" shape=point]'))

stdf$I[colSums(stdf$M!=0)==2] <- sapply(stdf$I[colSums(stdf$M!=0)==2],function(step)paste0('[label="',step,'" shape=diamond]'))
stdf$I[!is.na(stdf$o)] <- sapply(stdf$I[!is.na(stdf$o)],function(step)paste0('[label="',step,'" shape=parallelogram]'))
stdf$I[is.na(stdf$o)&colSums(stdf$M!=0)==1&rowSums(stdf$M!=0)!=0] <- as.vector(sapply(stdf$I[is.na(stdf$o)&colSums(stdf$M!=0)==1&rowSums(stdf$M!=0)!=0],function(step)paste0('[label="',step,'" shape=box]')))

stdf$I[colSums(stdf$M!=0)==0] <- sapply(stdf$I[colSums(stdf$M!=0)==0],function(step)paste0('[label="',step,'" shape=point]'))

#TODO : Refer to ``data.fram as V-V-matrix``
for(i in 1:length(stdf$I))stdf$I[[i]] <- paste0('"',i,' ',i,'"',stdf$I[[i]])
dot(as.character(paste0(stdf$I)))

false <- which(stdf$M==-1,arr.ind=TRUE)
false <- as.data.frame(matrix(c(t(false)),nrow=2))
dot('{edge[label="/F"]',sep='')
dot(as.character(lapply(false,function(yx)paste0('"',yx[2],' ',yx[2],'"','->','"',yx[1],' ',yx[1],'"'))),sep='')
dot('}',sep='')

true <- which(stdf$M==1,arr.ind=TRUE)
true <- as.data.frame(matrix(c(t(true)),nrow=2))
dot('{edge[label="/T"]',sep='')
dot(as.character(lapply(true,function(yx)paste0('"',yx[2],' ',yx[2],'"','->','"',yx[1],' ',yx[1],'"'))),sep='')
dot('}',sep='')

dot(sapply(which(!is.na(stdf$o)) , function(n){
	paste0('{rank=same',
	paste0('{"',n,' i"[label=""shape=none width=0 height=0]}->','"',n,' ',n,'"[label="',stdf$i[n],'"style=dashed]') ,
	paste0('"',n,' ',n,'"->','{"',n,' o"[label=""shape=none width=0 height=0]}','[label="',stdf$o[n],'"style=dashed]') ,
	'}')
}))

#library(xtable);dotdebug(xtable(coor,digits=0))

dot('}',sep='')
