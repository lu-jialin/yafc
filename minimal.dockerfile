FROM alpine

RUN apk add --no-cache R python3 py3-yaml

COPY ./yaml2r.py /root/
COPY ./r2dot.r /root/

WORKDIR /root
CMD sh -c 'cat | python3 ./yaml2r.py | R -s --no-save | Rscript ./r2dot.r $HOSTNAME'
