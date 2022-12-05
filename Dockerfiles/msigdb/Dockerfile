#stage for packaging transfomers
FROM python:3.8.1-alpine3.11 AS packaging-image
RUN mkdir -p /usr/src/base
COPY util/python/transformers-2.0 /usr/src/base
WORKDIR /usr/src/base
RUN python setup.py bdist_wheel
RUN mkdir -p /usr/src/msigdb
COPY transformers/msigdb/python-flask-server /usr/src/msigdb
WORKDIR /usr/src/msigdb
RUN python setup.py bdist_wheel
#stage for installing transformers on server
FROM python:3.8.1-alpine3.11 AS runtime-image
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/data
RUN mkdir -p /usr/src/app/info
COPY transformers/msigdb/python-flask-server/info /usr/src/app/info
WORKDIR /usr/src/app/data
COPY util/python/transformers-2.0/config/BiolinkClassMap.txt /usr/src/app/data
COPY util/python/transformers-2.0/config/prefixMap.json /usr/src/app/data
ADD https://translator.broadinstitute.org/db/MSigDB.sqlite /usr/src/app/data
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/base/dist .
COPY --from=packaging-image /usr/src/msigdb/dist .
RUN pip3 install -I msigdb_transfromer-2.3.0-py3-none-any.whl
RUN pip3 install -I base_transformer-2.0.0-py3-none-any.whl
COPY transformers/msigdb/python-flask-server/requirements.txt .
RUN apk update \
    && apk add --upgrade --no-cache \
        bash openssh curl ca-certificates openssl less htop \
        g++ make wget rsync \
        build-base libpng-dev freetype-dev libexecinfo-dev openblas-dev libgomp lapack-dev \
        libgcc libquadmath musl  \
        libgfortran \
        lapack-dev \
    &&  pip install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","2","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","1800"]
