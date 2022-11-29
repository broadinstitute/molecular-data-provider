## How to deploy DGIdb transformer

### Package transformer

Package transformer itself
```
cd transformers/dgidb/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/transformers-1.0
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/dgidb/python-flask-server/dist/dgidb_transformer-2.1.1-py3-none-any.whl` to the target folder

copy `util/python/transformers-1.0/dist/base_transformer-1.0.0-py3-none-any.whl` to the target folder

copy `transformers/dgidb/python-flask-server/info` folder to the target folder

download DGIdb.db from `https://translator.broadinstitute.org/db/DGIdb.db` and save to `data` subfolder of the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I dgidb_transformer-2.1.1-py3-none-any.whl
pip install -I base_transformer-1.0.0-py3-none-any.whl
pip install gunicorn
pip install "connexion[swagger-ui]"
deactivate
```

### Launch transformer

```
mkdir logs
source venv/bin/activate.csh
nohup gunicorn -w 2 -b 0.0.0.0:<port#> openapi_server.__main__:app --timeout 300 >& logs/openapi_server.log &
deactivate
```



