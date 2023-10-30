library(yaml)
y=yaml.load_file(input=commandArgs(trailingOnly=T)[1])
size<-function(y,size)
{
	sapply(y,function(y){
		size<-function(y,size)
		{
			if(!is.list(y)) 1
			else if(is.null(names(y)))
				sapply(y,function(y){size(y,size)})
			else
				sapply(names(y),function(n){size(y[[n]],size)})
		}
		size(y,size)
	})
}
size(y,size)
