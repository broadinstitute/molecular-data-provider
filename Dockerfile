#stage for packaging transfomers
FROM python:3-alpine AS packaging-image
RUN mkdir -p /usr/src/base
COPY util/python/transformers-2.0 /usr/src/base
WORKDIR /usr/src/base
RUN python setup.py bdist_wheel
RUN mkdir -p /usr/src/moleprodb
COPY transformers/molepro-db/python-flask-server /usr/src/moleprodb
WORKDIR /usr/src/moleprodb
RUN python setup.py bdist_wheel

#stage for installing transformers on server
FROM python:3-alpine AS runtime-image
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/data
RUN mkdir -p /usr/src/app/info
COPY transformers/molepro-db/python-flask-server/info /usr/src/app/info
WORKDIR /usr/src/app/data
COPY util/python/transformers-2.0/config/BiolinkClassMap.txt /usr/src/app/data
COPY util/python/transformers-2.0/config/prefixMap.json /usr/src/app/data
COPY transformers/molepro-db/python-flask-server/transformerConfig.json /usr/src/app/data
ADD https://translator.broadinstitute.org/db/MoleProDB.sqlite /usr/src/app/data
ADD https://translator.broadinstitute.org/db/moleprodb_name_producer_info.json /usr/src/app/data
ADD https://translator.broadinstitute.org/db/moleprodb_producer_info.json /usr/src/app/data
ADD https://translator.broadinstitute.org/db/moleprodb_transformer_info.json /usr/src/app/data
ADD https://translator.broadinstitute.org/db/moleprodb_hierarchy_transformer_info.json /usr/src/app/data
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/base/dist .
COPY --from=packaging-image /usr/src/moleprodb/dist .
RUN pip3 install -I moleprodb_transformer-2.4.3-py3-none-any.whl
RUN pip3 install -I base_transformer-2.0.0-py3-none-any.whl
COPY transformers/molepro-db/python-flask-server/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","128","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","600"]
