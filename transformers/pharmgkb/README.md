## How to deploy PharmGKB transformer

### Package transformer

Package transformer itself
```
cd transformers/pharmgkb/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/transformers-2.5
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/pharmgkb/python-flask-server/dist/pharmgkb_transformer-2.5.1-py3-none-any.whl` to the target folder

copy `util/python/transformers-2.5/dist/base_transformer-2.5.1-py3-none-any.whl` to the target folder

copy `transformers/pharmgkb/python-flask-server/info` folder to the target folder

download pharmgkb.sqlite from `https://translator.broadinstitute.org/db/pharmgkb.sqlite` and save to `data` subfolder of the target folder

### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I pharmgkb_transformer-2.5.1-py3-none-any.whl
pip install -I base_transformer-2.5.1-py3-none-any.whl
pip install gunicorn
pip install "connexion[swagger-ui]"
deactivate
```

### Launch transformer

```
mkdir logs
source venv/bin/activate.csh
nohup gunicorn -w 16 -b 0.0.0.0:<port#> openapi_server.__main__:app --timeout 300 >& logs/openapi_server.log &
deactivate
```
