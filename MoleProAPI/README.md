## How to deploy MolePro

### Package MolePro

```
cd MoleProAPI/java-play-framework-server
sbt universal:packageZipTarball
```

### Copy files to server

copy molecular-data-provider-2.4.1.tgz to target folder

### unpack MolePro

```
gunzip molecular-data-provider-2.4.1.tgz
tar xf molecular-data-provider-2.4.1.tar
```

### start MolePro

set environment variable MOLEPRO_HOST = https://molepro.ci.transltr.io/molecular_data_provider

set environment variable MOLEPRO_TRANSFORMERS = conf/dockerTransformers.txt

./bin/molecular-data-provider -J-Xmx4096m -Dplay.http.secret.key='{passrowd}' -Dhttp.port=9200
