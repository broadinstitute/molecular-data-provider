package controllers;

import apimodels.AggregationQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.ComparisonInfo;
import apimodels.ErrorMsg;

import play.mvc.Http;
import transformer.collection.Collections;
import transformer.collection.Comparison;
import transformer.collection.Aggregator;

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
        return Aggregator.aggregate(aggregationQuery, cache);
    }

    @Override
    public Collection collectionCollectionIdGet(Http.Request request, String collectionId, String cache) throws Exception {
        return Collections.getCollection(collectionId, cache).asCollection();
    }

    @Override
	public ComparisonInfo comparePost(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception {
		return Comparison.compare(aggregationQuery, cache);
	}

}
