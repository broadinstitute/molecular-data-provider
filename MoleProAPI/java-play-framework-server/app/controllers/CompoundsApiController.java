package controllers;

import apimodels.CollectionInfo;
import apimodels.CompoundInfo;
import apimodels.CompoundList;
import apimodels.ErrorMsg;
import java.util.List;

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


public class CompoundsApiController extends Controller {

    private final CompoundsApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Configuration configuration;

    @Inject
    private CompoundsApiController(Configuration configuration, CompoundsApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }


    @ApiAction
    public Result compoundByIdCompoundIdGet(String compoundId) throws Exception {
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        CompoundInfo obj = imp.compoundByIdCompoundIdGet(compoundId, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result compoundByIdPost() throws Exception {
        JsonNode noderequestBody = request().body().asJson();
        List<String> requestBody;
        if (noderequestBody != null) {
            requestBody = mapper.readValue(noderequestBody.toString(), new TypeReference<List<String>>(){});
            if (configuration.getBoolean("useInputBeanValidation")) {
                for (String curItem : requestBody) {
                    OpenAPIUtils.validate(curItem);
                }
            }
        } else {
            throw new IllegalArgumentException("'request_body' parameter is required");
        }
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        CollectionInfo obj = imp.compoundByIdPost(requestBody, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result compoundByNameNameGet(String name) throws Exception {
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        CompoundList obj = imp.compoundByNameNameGet(name, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result compoundByNamePost() throws Exception {
        JsonNode noderequestBody = request().body().asJson();
        List<String> requestBody;
        if (noderequestBody != null) {
            requestBody = mapper.readValue(noderequestBody.toString(), new TypeReference<List<String>>(){});
            if (configuration.getBoolean("useInputBeanValidation")) {
                for (String curItem : requestBody) {
                    OpenAPIUtils.validate(curItem);
                }
            }
        } else {
            throw new IllegalArgumentException("'request_body' parameter is required");
        }
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        CollectionInfo obj = imp.compoundByNamePost(requestBody, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result compoundByStructurePost() throws Exception {
        JsonNode nodebody = request().body().asJson();
        String body;
        if (nodebody != null) {
            body = mapper.readValue(nodebody.toString(), String.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(body);
            }
        } else {
            throw new IllegalArgumentException("'body' parameter is required");
        }
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        CompoundInfo obj = imp.compoundByStructurePost(body, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }
}
