## How to deploy GWAS transformer

### Package transformer

Package transformer itself
```
cd transformers/gwas/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd ../../../util/python/transformers-2.0
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/gwas/python-flask-server/dist/gwas_transformer-2.4.0-py2-none-any.whl` to the target folder

copy `util/python/transformers-2.0/dist/base_transformer-2.0.1-py2-none-any.whl` to the target folder

copy `transformers/gwas/python-flask-server/info` folder to the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I gwas_transformer-2.4.0-py2-none-any.whl
pip install -I base_transformer-2.0.1-py2-none-any.whl
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
