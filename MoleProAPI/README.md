## How to deploy MolePro

### Package MolePro

```
cd MoleProAPI/java-play-framework-server
sbt universal:packageZipTarball
```

### Copy files to server
```
copy molecular-data-provider-2.4.1.tgz to target folder
cd target
```

### unpack MolePro

```
gunzip molecular-data-provider-2.4.1.tgz
tar xf molecular-data-provider-2.4.1.tar
```

### start MolePro

#### for CI (Continuous Integration) environment only:
* set environment variable MOLEPRO_HOST = https://molepro.ci.transltr.io/molecular_data_provider

* set environment variable MOLEPRO_TRANSFORMERS = conf/dockerTransformers.txt

#### for Test environment only:
* set environment variable MOLEPRO_HOST = https://molepro.test.transltr.io/molecular_data_provider

* set environment variable MOLEPRO_TRANSFORMERS = conf/dockerTransformers-test.txt

#### for Production environment only:
* set environment variable MOLEPRO_HOST = https://molepro.transltr.io/molecular_data_provider

* set environment variable MOLEPRO_TRANSFORMERS = conf/dockerTransformers-prod.txt

#### for all environments (CI, Test and Production):
* cd molecular-data-provider-2.4.1

* ./bin/molecular-data-provider -J-Xmx4096m -Dplay.http.secret.key='_{passrowd}_' -Dhttp.port=9200
 
   #### (be sure to replace _{passrowd}_ with an actual secret key, any random string generated and documented but not to be saved in GitHub)






## In Case of java.lang.UnsupportedClassVersionError

The error is caused by the incompatibility between the MolePro API compiled with Java 17 and Java Runtime Engine 1.8, (A reference about "class file version",  https://www.baeldung.com/java-lang-unsupportedclassversion):

_Exception in thread "main" java.lang.UnsupportedClassVersionError: Module has been compiled by a more recent version of the Java Runtime (class file version 61.0), this version of the Java Runtime only recognizes class file versions up to 52.0_



To work around that error condition, compile MolePro API with 1.8, which can be done with the following steps:



1. Make sure that your computer has switched to Java 1.8 by running the "java -version" command:

% java -version

openjdk version "1.8.0_312"

OpenJDK Runtime Environment (build 1.8.0_312-bre_2021_10_20_23_15-b00)

OpenJDK 64-Bit Server VM (build 25.312-b00, mixed mode)



if not, then refer to the guidance given here https://mkyong.com/java/how-to-install-java-on-mac-osx/#switch-between-different-jdk-versions



2.  Change to this directory: /MoleProAPI/java-play-framework-server



3.  Run this following command:
**sbt clean compile shell**

which will start a Java 1.8 compile of MolePro API as indicated by this message: 

[info] welcome to sbt 1.3.13 (Homebrew Java 1.8.0_312)

[info] loading settings for project java-play-framework-server-build from plugins.sbt ...




and end with a successful completion of the compile indicated by a message similar to this:
 [success] Total time: 16 s, completed Nov 23, 2021 8:19:19 AM



4.  Hit "control-C" to terminate the sbt session started in step #3.

5.  Proceed to do the **How to deploy MolePro** steps 
