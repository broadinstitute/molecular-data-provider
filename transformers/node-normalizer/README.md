## How to deploy node-normalizer transformer

### Package transformer

Package transformer itself
```
cd transformers/node-normalizer/python-flask-server
python setup.py bdist_wheel
```
Package transformer base class
```
cd util/python/
python setup.py bdist_wheel
```

### Copy files to server

copy `transformers/node-normalizer/python-flask-server/dist/node_normalizer_transformer-2.3.0-py3-none-any.whl` to the target folder

copy `util/python/dist/base_transformer-1.0.0-py3-none-any.whl` to the target folder

copy `transformers/node-normalizer/python-flask-server/info` folder to the target folder

copy `MoleProAPI/java-play-framework-server/conf/BiolinkClassMap.txt` to `data` subfolder of the target folder

copy `MoleProAPI/java-play-framework-server/conf/prefixMap.json` to `data` subfolder of the target folder

### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I node_normalizer_transformer-2.3.0-py3-none-any.whl
pip install -I base_transformer-1.0.0-py3-none-any.whl
pip install gunicorn
pip install "connexion[swagger-ui]"
deactivate
```

### Launch transformer

```
mkdir logs
source venv/bin/activate.csh
nohup gunicorn -w 2 -b 0.0.0.0:<port#> openapi_server.__main__:app --timeout 1800 >& logs/openapi_server.log &
deactivate
```
