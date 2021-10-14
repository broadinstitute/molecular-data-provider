## How to deploy HMDB transformer

### Package transformer

Package transformer itself
```
cd transformers/hmdb/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/transformers-1.0
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/hmdb/python-flask-server/dist/hmdb_transformer-2.2.0-py3-none-any.whl` to the target folder

copy `util/python/transformers-1.0/dist/base_transformer-1.0.0-py3-none-any.whl` to the target folder

copy `transformers/hmdb/python-flask-server/info` folder to the target folder

download HMDB-KS.db from `https://translator.broadinstitute.org/db/HMDB-KS.db` and save to `data` subfolder of the target folder
download UniProt2Entrez.txt from https://translator.broadinstitute.org/db/UniProt2Entrez.txt


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I hmdb_transformer-2.2.0-py3-none-any.whl
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



