#stage for sbt packaging 
FROM bpatters/docker-java8-sbt AS packaging-image
RUN mkdir -p /usr/src/base
RUN mkdir -p /usr/src/base/lib
COPY transformers/gelinea/java-play-framework-server /usr/src/base
ADD https://translator.broadinstitute.org/db/gelinea/gelinea.jar /usr/src/base/lib
WORKDIR /usr/src/base
RUN sbt playUpdateSecret
RUN sbt universal:packageZipTarball

#stage for installing transformers on server
FROM adoptopenjdk/openjdk8:latest AS runtime-image
RUN mkdir -p /usr/src/target
WORKDIR /usr/src/target
COPY --from=packaging-image /usr/src/base/target/universal/gelinea-transformer-2.5.0.tgz /usr/src/target
RUN gunzip gelinea-transformer-2.5.0.tgz
RUN tar xf gelinea-transformer-2.5.0.tar
WORKDIR /usr/src/target/gelinea-transformer-2.5.0
RUN mkdir data
ADD https://translator.broadinstitute.org/db/gelinea/c2.all.current.STRING.gmt data/c2.all.current.STRING.gmt
ADD https://translator.broadinstitute.org/db/gelinea/c5.all.current.STRING.gmt data/c5.all.current.STRING.gmt
ADD https://translator.broadinstitute.org/db/gelinea/h.all.current.STRING.gmt data/h.all.current.STRING.gmt
ADD https://translator.broadinstitute.org/db/gelinea/human.links_400.txt data/human.links_400.txt
ADD https://translator.broadinstitute.org/db/gelinea/human.links_700.txt data/human.links_700.txt
ADD https://translator.broadinstitute.org/db/gelinea/human_GeneID.txt data/human_GeneID.txt
EXPOSE 8290
CMD ["./bin/gelinea-transformer", "-J-Xmx4096m", "-Dhttp.port=8080"]
