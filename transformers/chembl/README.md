## How to deploy ChEMBL transformer

### Package transformer

Package transformer itself
```
cd transformers/chembl/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/transformers-2.0
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/chembl/python-flask-server/dist/chembl_transformer-2.4.0-py3-none-any.whl` to the target folder

copy `util/python/transformers-2.0/dist/base_transformer-2.0.1-py3-none-any.whl` to the target folder

copy `util/python/transformers-2.0/config/BiolinkClassMap.txt` to `data` subfolder of the target folder

copy `util/python/transformers-2.0/config/prefixMap.json` to `data` subfolder of the target folder

copy `transformers/chembl/python-flask-server/info` folder to the target folder

download ChEMBL.sqlite from `https://translator.broadinstitute.org/db/ChEMBL.sqlite` and save to `data` subfolder of the target folder

download ChEMBL.target.xref.sqlite from `https://translator.broadinstitute.org/db/ChEMBL.target.xref.sqlite` and save to `data` subfolder of the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I chembl_transformer-2.4.0-py3-none-any.whl
pip install -I base_transformer-2.0.1-py3-none-any.whl
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



