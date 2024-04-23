## How to deploy CTRP transformer

### Package transformer

Package transformer itself
```
cd transformers/ctrp/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/ctrp/python-flask-server/dist/ctrp_transformer-2.2.0-py3-none-any.whl` to the target folder

copy `util/python/dist/base_transformer-1.0.0-py3-none-any.whl` to the target folder

copy `transformers/ctrp/python-flask-server/ctrp_transformer_info.json` folder to the target folder

download CTRP.sqlite from `https://translator.broadinstitute.org/db/CTRP.sqlite` and save to `data` subfolder of the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I ctrp_transformer-2.2.0-py3-none-any.whl
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



