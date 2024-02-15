#stage for sbt packaging 
FROM bpatters/docker-java8-sbt AS packaging-image
RUN mkdir -p /usr/src/base
COPY MoleProAPI/java-play-framework-server /usr/src/base
WORKDIR /usr/src/base
RUN sbt universal:packageZipTarball
#stage for installing transformers on server
FROM adoptopenjdk/openjdk8:latest AS runtime-image
RUN mkdir -p /usr/src/target
WORKDIR /usr/src/target
COPY --from=packaging-image /usr/src/base/target/universal/molecular-data-provider-2.5.1.tgz /usr/src/target
RUN gunzip molecular-data-provider-2.5.1.tgz
RUN tar xf molecular-data-provider-2.5.1.tar
WORKDIR /usr/src/target/molecular-data-provider-2.5.1
EXPOSE 9200
CMD ["./bin/molecular-data-provider", "-J-Xmx4096m", "-Dplay.http.secret.key='{passrowd}'", "-Dhttp.port=9200"]
