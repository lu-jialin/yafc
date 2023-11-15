FROM m4_base()
RUN apt update
RUN apt install -y --no-install-recommends r-base-core  && apt-get clean autoclean && apt-get autoremove --yes
RUN apt install -y --no-install-recommends graphviz     && apt-get clean autoclean && apt-get autoremove --yes
RUN apt install -y --no-install-recommends python3-yaml && apt-get clean autoclean && apt-get autoremove --yes

COPY ./yaml2r.py /root/
COPY ./r2dot.r /root/

WORKDIR /root
CMD sh -c 'cat | python3 ./yaml2r.py | R -s --no-save | Rscript ./r2dot.r $HOSTNAME | dot -T`'m4_type()'
