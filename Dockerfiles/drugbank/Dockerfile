#stage for packaging transfomers
FROM python:3-alpine AS packaging-image
RUN mkdir -p /usr/src/base
COPY util/python /usr/src/base
WORKDIR /usr/src/base
RUN python setup.py bdist_wheel
RUN mkdir -p /usr/src/drugbank
COPY transformers/drugbank/python-flask-server /usr/src/drugbank
WORKDIR /usr/src/drugbank
RUN python setup.py bdist_wheel

#stage for installing transformers on server
FROM python:3-alpine AS runtime-image
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/info
COPY transformers/drugbank/python-flask-server/info /usr/src/app/info
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/base/dist .
COPY --from=packaging-image /usr/src/drugbank/dist .
RUN pip3 install -I base_transformer-1.0.0-py3-none-any.whl
RUN pip3 install -I drugbank_transformer-2.4.0-py3-none-any.whl
RUN mkdir -p /usr/src/app/data
WORKDIR /usr/src/app/data
COPY transformers/drugbank/python-flask-server/data/prefixMap.csv .
COPY MoleProAPI/java-play-framework-server/conf/BiolinkClassMap.txt .
COPY MoleProAPI/java-play-framework-server/conf/prefixMap.json .
ADD https://translator.broadinstitute.org/db/DrugBank.sqlite .
COPY transformers/drugbank/python-flask-server/requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","2","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","1800"]
