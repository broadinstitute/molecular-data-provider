#stage for packaging transfomers
FROM python:3-alpine AS packaging-image
RUN mkdir -p /usr/src/base
COPY util/python/transformers-2.0 /usr/src/base
WORKDIR /usr/src/base
RUN python setup.py bdist_wheel
RUN mkdir -p /usr/src/hmdb
COPY transformers/hmdb/python-flask-server /usr/src/hmdb
WORKDIR /usr/src/hmdb
RUN python setup.py bdist_wheel
#stage for installing transformers on server
FROM python:3-alpine AS runtime-image
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/data
RUN mkdir -p /usr/src/app/info
COPY transformers/hmdb/python-flask-server/info /usr/src/app/info
WORKDIR /usr/src/app/data
COPY util/python/transformers-2.0/config/BiolinkClassMap.txt /usr/src/app/data
COPY util/python/transformers-2.0/config/prefixMap.json /usr/src/app/data
ADD https://translator.broadinstitute.org/db/HMDB.sqlite /usr/src/app/data
ADD https://translator.broadinstitute.org/db/UniProt2Entrez.txt /usr/src/app/data
ADD https://translator.broadinstitute.org/db/HMDB-term.tsv /usr/src/app/data
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/base/dist .
COPY --from=packaging-image /usr/src/hmdb/dist .
RUN pip3 install -I hmdb_transformer-2.4.0-py3-none-any.whl
RUN pip3 install -I base_transformer-2.0.1-py3-none-any.whl
COPY transformers/hmdb/python-flask-server/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","2","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","1800"]