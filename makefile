.PHONY: docker
@:
	false
docker: svg pdf
svg: svg.dockerfile
	docker build -f $@.dockerfile -t lujialin/yafc:$@ .
pdf: pdf.dockerfile
	docker build -f $@.dockerfile -t lujialin/yafc:$@ .
