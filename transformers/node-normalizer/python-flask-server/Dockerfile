FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY /util/python/ /usr/src/app/
RUN python setup.py bdist_wheel

WORKDIR /usr/src/app/dist
RUN pip3 install -I base_transformer-1.0.0-py3-none-any.whl

RUN mkdir -p /usr/src/app/data
WORKDIR /usr/src/app/data
COPY /MoleProAPI/java-play-framework-server/conf/BiolinkClassMap.txt /usr/src/app/data
COPY /MoleProAPI/java-play-framework-server/conf/prefixMap.json /usr/src/app/data

WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/

WORKDIR /usr/src/app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8430

ENTRYPOINT ["python3"]

CMD ["-m", "openapi_server"]