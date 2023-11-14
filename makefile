.PHONY: docker
@:
	false
docker: dot
svg: svg.dockerfile
	docker build -f $@.dockerfile -t lujialin/yafc:$@ .
pdf: pdf.dockerfile
	docker build -f $@.dockerfile -t lujialin/yafc:$@ .
dot: dot.dockerfile
	docker build -f $@.dockerfile -t lujialin/yafc:$@ .
