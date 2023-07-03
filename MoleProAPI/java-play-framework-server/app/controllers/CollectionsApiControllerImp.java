package controllers;

import apimodels.AggregationQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.ComparisonInfo;
import apimodels.ErrorMsg;

import play.mvc.Http;
import transformer.classes.Compound;
import transformer.classes.Gene;
import transformer.collection.Collections;

import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.io.FileInputStream;
import play.libs.Files.TemporaryFile;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
public class CollectionsApiControllerImp extends CollectionsApiControllerImpInterface {
    @Override
    public CollectionInfo aggregatePost(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public Collection collectionCollectionIdGet(Http.Request request, String collectionId, String cache) throws Exception {
        return Collections.getCollection(collectionId, cache).asCollection();
    }

    @Override
    public ComparisonInfo comparePost(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception {
        //Do your magic!!!
        return new ComparisonInfo();
    }

}
