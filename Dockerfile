#stage for packaging transfomers
FROM python:3-alpine AS packaging-image
RUN mkdir -p /usr/src/reasonerAPI
COPY reasonerAPI/python-flask-server /usr/src/reasonerAPI
WORKDIR /usr/src/reasonerAPI
RUN python setup.py bdist_wheel
#stage for installing transformers on server
FROM python:3-alpine AS runtime-image
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/reasonerAPI/dist .
RUN pip3 install -I molepro_trapi-1.3.0.1-py3-none-any.whl
COPY reasonerAPI/python-flask-server .
COPY reasonerAPI/python-flask-server/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","128","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","600"]
