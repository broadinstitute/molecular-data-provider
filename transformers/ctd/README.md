## How to deploy CTD transformer

### Package transformer

Package transformer itself
```
cd transformers/ctd/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/ctd/python-flask-server/dist/ctd_transformer-2.3.0-py3-none-any.whl` to the target folder

copy `util/python/transformers-2.0/dist/base_transformer-2.0.0-py3-none-any.whl` to the target folder

copy `transformers/ctd/python-flask-server/info` folder to the target folder

copy `util/python/transformers-2.0/config/BiolinkClassMap-2.txt` to `data` subfolder of the target folder

copy `util/python/transformers-2.0/config/prefixMap-2.json` to `data` subfolder of the target folder

download CTD.sqlite from `https://translator.broadinstitute.org/db/CTD.sqlite` and save to `data` subfolder of the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I ctd_transformer-2.3.0-py3-none-any.whl
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
