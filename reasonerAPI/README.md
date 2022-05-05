## How to deploy reasonerAPI

### Package transformer

Package transformer itself
```
cd reasonerAPI/python-flask-server
python setup.py bdist_wheel
```

### Copy files to server

copy `reasonerAPI/python-flask-server/dist/molepro_trapi-1.2.1.3-py3-none-any.whl` to the target folder


### Install transformer on server

```
python3 -m venv venv
source venv/bin/activate.csh
pip install -I molepro_trapi-1.2.1.3-py3-none-any.whl
pip install gunicorn
pip install "connexion[swagger-ui]"
deactivate
```

### Launch transformer

```
set environment variable MOLEPRO_QUERY_LIMIT 1000
set environment variable MOLEPRO_PORT <port#>
set environment variable MOLEPRO_BASE_URL https://molepro.ci.transltr.io/molecular_data_provider
set environment variable MOLEPRO_URL_BIOLINK https://bl-lookup-sri.renci.org/bl
set environment variable MOLEPRO_URL_TRANSFORMERS https://molepro.ci.transltr.io/molecular_data_provider/transformers
```

```
mkdir logs
source venv/bin/activate.csh
nohup gunicorn -w 6 -b 0.0.0.0:<port#> openapi_server.__main__:app --timeout 600 >& logs/openapi_server.log &
deactivate
```
