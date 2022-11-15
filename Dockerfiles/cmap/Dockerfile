#stage for packaging transfomers
FROM python:3-alpine AS packaging-image
RUN mkdir -p /usr/src/base
COPY util/python /usr/src/base
WORKDIR /usr/src/base
RUN python setup.py bdist_wheel
RUN mkdir -p /usr/src/cmap
COPY transformers/cmap/python-flask-server /usr/src/cmap
WORKDIR /usr/src/cmap
RUN python setup.py bdist_wheel

#stage for installing transformers on server
FROM python:3-alpine AS runtime-image
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/data
ADD https://translator.broadinstitute.org/db/CMAP_pert_ids.txt /usr/src/app/data
WORKDIR /usr/src/app
COPY --from=packaging-image /usr/src/base/dist .
COPY --from=packaging-image /usr/src/cmap/dist .
RUN pip3 install -I base_transformer-1.0.0-py3-none-any.whl
RUN pip3 install -I cmap_transformer-2.1.1-py3-none-any.whl
COPY transformers/cmap/python-flask-server/transformer_info.json .
COPY transformers/cmap/python-flask-server/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["nohup","gunicorn", "-w","2","-b","0.0.0.0:8080","openapi_server.__main__:app","--timeout","1800"]
