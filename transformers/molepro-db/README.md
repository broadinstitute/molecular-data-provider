## How to deploy moleprodb transformer

### Package transformer

Package transformer itself
```
cd transformers/moleprodb/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/moleprodb/python-flask-server/dist/moleprodb_transformer-2.3.0-py3-none-any.whl` to the target folder

copy `util/python/transformers-2.0/dist/base_transformer-2.0.0-py3-none-any.whl` to the target folder

copy `transformers/moleprodb/python-flask-server/info` folder to the target folder

copy `util/python/transformers-2.0/config/BiolinkClassMap.txt` to `data` subfolder of the target folder

copy `util/python/transformers-2.0/config/prefixMap.json` to `data` subfolder of the target folder

copy 'transformers/moleprodb/python-flask-server/transformerConfig.json' to `data` subfolder of the target folder

download MoleProDB.sqlite from `https://translator.broadinstitute.org/db/MoleProDB.sqlite` and save to `data` subfolder of the target folder


download moleprodb_name_producer_info.json from `https://translator.broadinstitute.org/db/moleprodb_name_producer_info.json` and save to `data` subfolder of the target folder

download moleprodb_producer_info.json from `https://translator.broadinstitute.org/db/moleprodb_producer_info.json` and save to `data` subfolder of the target folder

download moleprodb_transformer_info.json from `https://translator.broadinstitute.org/db/moleprodb_transformer_info.json` and save to `data` subfolder of the target folder

**download moleprodb_hierarchy_transformer_info.json from 'https://translator.broadinstitute.org/db/moleprodb_hierarchy_transformer_info.json' and save to ‘data’ subfolder of the target folder**

### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I moleprodb_transformer-2.3.0-py3-none-any.whl
pip install -I base_transformer-2.0.0-py3-none-any.whl
pip install gunicorn
pip install "connexion[swagger-ui]"
deactivate
```

### Launch transformer

```
mkdir logs
source venv/bin/activate.csh
nohup gunicorn -w 4 -b 0.0.0.0:<port#> openapi_server.__main__:app --timeout 600 >& logs/openapi_server.log &
deactivate
```
