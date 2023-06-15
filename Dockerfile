#stage for packaging transfomers
FROM python:3-alpine AS packaging-image
RUN mkdir -p /usr/src/base
COPY util/python/transformers-2.5 /usr/src/base
WORKDIR /usr/src/base
RUN python setup.py bdist_wheel
RUN mkdir -p /usr/src/node-normalizer
COPY transformers/node-normalizer/python-flask-server /usr/src/node-normalizer
WORKDIR /usr/src/node-normalizer
RUN python setup.py bdist_wheel

#stage for installing transformers on server
FROM python:3-alpine AS runtime-image
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/info
COPY transformers/node-normalizer/python-flask-server/info /usr/src/app/info
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/base/dist .
COPY --from=packaging-image /usr/src/node-normalizer/dist .
RUN pip3 install -I base_transformer-2.5.0-py3-none-any.whl
RUN pip3 install -I node_normalizer_transformer-2.5.0-py3-none-any.whl
RUN mkdir -p /usr/src/app/data
WORKDIR /usr/src/app/data
COPY MoleProAPI/java-play-framework-server/conf/BiolinkClassMap.txt .
COPY MoleProAPI/java-play-framework-server/conf/prefixMap.json .
COPY transformers/node-normalizer/python-flask-server/requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","32","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","300"]
