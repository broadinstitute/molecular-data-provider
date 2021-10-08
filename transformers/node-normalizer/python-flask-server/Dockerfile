FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY /util/python/ /usr/src/app/
RUN python setup.py bdist_wheel

WORKDIR /usr/src/app/dist
COPY node_normalizer_transformer-2.3.0-py3-none-any.whl /usr/src/app/dist
RUN pip3 install -I base_transformer-1.0.0-py3-none-any.whl
RUN pip3 install -I node_normalizer_transformer-2.3.0-py3-none-any.whl
RUN mkdir -p /usr/src/app/data
WORKDIR /usr/src/app/data
COPY /MoleProAPI/java-play-framework-server/conf/BiolinkClassMap.txt /usr/src/app/data
COPY /MoleProAPI/java-play-framework-server/conf/prefixMap.json /usr/src/app/data

WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/

WORKDIR /usr/src/app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

CMD ["nohup","gunicorn", "-w","2","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","1800"]