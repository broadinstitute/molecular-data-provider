package controllers;

import apimodels.AggregationQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.ComparisonInfo;
import apimodels.ErrorMsg;

import com.google.inject.Inject;
import com.typesafe.config.Config;
import play.mvc.Controller;
import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import play.mvc.Result;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import openapitools.OpenAPIUtils;
import openapitools.SecurityAPIUtils;
import static play.mvc.Results.ok;
import static play.mvc.Results.unauthorized;
import play.libs.Files.TemporaryFile;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public abstract class CollectionsApiControllerImpInterface {
    @Inject private Config configuration;
    @Inject private SecurityAPIUtils securityAPIUtils;
    private ObjectMapper mapper = new ObjectMapper();

    public Result aggregatePostHttp(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception {
        CollectionInfo obj = aggregatePost(request, aggregationQuery, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract CollectionInfo aggregatePost(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception;

    public Result collectionCollectionIdGetHttp(Http.Request request, String collectionId, String cache) throws Exception {
        Collection obj = collectionCollectionIdGet(request, collectionId, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract Collection collectionCollectionIdGet(Http.Request request, String collectionId, String cache) throws Exception;

    public Result comparePostHttp(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception {
        ComparisonInfo obj = comparePost(request, aggregationQuery, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract ComparisonInfo comparePost(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception;

}
