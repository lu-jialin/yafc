FROM alpine

RUN apk add --no-cache R python3 py3-pip
RUN pip install --no-cache-dir pyyaml

COPY ./yaml2r.py /root/
COPY ./r2dot.r /root/

RUN apk add --no-cache graphviz

CMD sh -c 'cat | python3 /root/yaml2r.py | R -s --no-save | Rscript /root/r2dot.r $HOSTNAME | dot -T svg'
