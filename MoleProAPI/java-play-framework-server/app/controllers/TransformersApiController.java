package controllers;

import apimodels.AggregationQuery;
import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import apimodels.MoleProQuery;
import apimodels.TransformerInfo;

import play.mvc.Controller;
import play.mvc.Result;
import play.mvc.Http;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.inject.Inject;
import java.io.File;
import openapitools.OpenAPIUtils;
import com.fasterxml.jackson.core.type.TypeReference;

import javax.validation.constraints.*;
import play.Configuration;

import openapitools.OpenAPIUtils.ApiAction;


public class TransformersApiController extends Controller {

    private final TransformersApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Configuration configuration;

    @Inject
    private TransformersApiController(Configuration configuration, TransformersApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }


    @ApiAction
    public Result aggregatePost() throws Exception {
        JsonNode nodeaggregationQuery = request().body().asJson();
        AggregationQuery aggregationQuery;
        if (nodeaggregationQuery != null) {
            aggregationQuery = mapper.readValue(nodeaggregationQuery.toString(), AggregationQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(aggregationQuery);
            }
        } else {
            throw new IllegalArgumentException("'AggregationQuery' parameter is required");
        }
        CollectionInfo obj = imp.aggregatePost(aggregationQuery);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result transformPost() throws Exception {
        JsonNode nodemoleProQuery = request().body().asJson();
        MoleProQuery moleProQuery;
        if (nodemoleProQuery != null) {
            moleProQuery = mapper.readValue(nodemoleProQuery.toString(), MoleProQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(moleProQuery);
            }
        } else {
            throw new IllegalArgumentException("'MoleProQuery' parameter is required");
        }
        CollectionInfo obj = imp.transformPost(moleProQuery);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result transformersGet() throws Exception {
        List<TransformerInfo> obj = imp.transformersGet();
        if (configuration.getBoolean("useOutputBeanValidation")) {
            for (TransformerInfo curItem : obj) {
                OpenAPIUtils.validate(curItem);
            }
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }
}
