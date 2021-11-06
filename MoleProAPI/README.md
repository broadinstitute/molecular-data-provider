## How to deploy MolePro

### Package MolePro

```
cd MoleProAPI/java-play-framework-server
sbt universal:packageZipTarball
```

### Copy files to server

copy molecular-data-provider-2.4.0.tgz to target folder

### unpack MolePro

```
gunzip molecular-data-provider-2.4.0.tgz
tar xf molecular-data-provider-2.4.0.tar
```

update base url in conf/transformerConfig.json to reflect deployed url

### start MolePro

generate {random string}:
  
```
sbt playGenerateSecret
```

./bin/molecular-data-provider -J-Xmx4096m -Dplay.http.secret.key='{random string}' -Dhttp.port=9200
