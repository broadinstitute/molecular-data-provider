## How to deploy ChEBI transformer

### Package transformer

Package transformer itself
```
cd transformers/chebi/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/chebi/python-flask-server/dist/chebi_transformer-2.3.0-py3-none-any.whl` to the target folder

copy `util/python/transformers-2.0/dist/base_transformer-2.0.0-py3-none-any.whl` to the target folder

copy `transformers/chebi/python-flask-server/info` folder to the target folder

copy `util/python/transformers-2.0/config/BiolinkClassMap.txt` to `data` subfolder of the target folder

copy `util/python/transformers-2.0/config/prefixMap.json` to `data` subfolder of the target folder

download ChEBI.sqlite from `https://translator.broadinstitute.org/db/ChEBI.sqlite` and save to `data` subfolder of the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I chebi_transformer-2.3.0-py3-none-any.whl
pip install -I base_transformer-2.0.0-py3-none-any.whl
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
