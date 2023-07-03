package controllers;

import apimodels.AggregationQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.ComparisonInfo;
import apimodels.ErrorMsg;

import com.typesafe.config.Config;
import play.mvc.Controller;
import play.mvc.Result;
import play.mvc.Http;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.inject.Inject;
import java.io.File;
import play.libs.Files.TemporaryFile;
import openapitools.OpenAPIUtils;
import com.fasterxml.jackson.core.type.TypeReference;

import javax.validation.constraints.*;
import com.typesafe.config.Config;

import openapitools.OpenAPIUtils.ApiAction;

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
public class CollectionsApiController extends Controller {
    private final CollectionsApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Config configuration;

    @Inject
    private CollectionsApiController(Config configuration, CollectionsApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }

    @ApiAction
    public Result aggregatePost(Http.Request request) throws Exception {
        JsonNode nodeaggregationQuery = request.body().asJson();
        AggregationQuery aggregationQuery;
        if (nodeaggregationQuery != null) {
            aggregationQuery = mapper.readValue(nodeaggregationQuery.toString(), AggregationQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(aggregationQuery);
            }
        } else {
            throw new IllegalArgumentException("'AggregationQuery' parameter is required");
        }
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.aggregatePostHttp(request, aggregationQuery, cache);
    }

    @ApiAction
    public Result collectionCollectionIdGet(Http.Request request, String collectionId) throws Exception {
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.collectionCollectionIdGetHttp(request, collectionId, cache);
    }

    @ApiAction
    public Result comparePost(Http.Request request) throws Exception {
        JsonNode nodeaggregationQuery = request.body().asJson();
        AggregationQuery aggregationQuery;
        if (nodeaggregationQuery != null) {
            aggregationQuery = mapper.readValue(nodeaggregationQuery.toString(), AggregationQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(aggregationQuery);
            }
        } else {
            throw new IllegalArgumentException("'AggregationQuery' parameter is required");
        }
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.comparePostHttp(request, aggregationQuery, cache);
    }

}
