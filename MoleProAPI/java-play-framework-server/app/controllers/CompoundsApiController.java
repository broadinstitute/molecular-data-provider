package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.ErrorMsg;
import java.util.List;

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
public class CompoundsApiController extends Controller {
    private final CompoundsApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Config configuration;

    @Inject
    private CompoundsApiController(Config configuration, CompoundsApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }

    @ApiAction
    public Result compoundByIdCompoundIdGet(Http.Request request, String compoundId) throws Exception {
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.compoundByIdCompoundIdGetHttp(request, compoundId, cache);
    }

    @ApiAction
    public Result compoundByIdPost(Http.Request request) throws Exception {
        JsonNode noderequestBody = request.body().asJson();
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
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.compoundByIdPostHttp(request, requestBody, cache);
    }

    @ApiAction
    public Result compoundByNameNameGet(Http.Request request, String name) throws Exception {
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.compoundByNameNameGetHttp(request, name, cache);
    }

    @ApiAction
    public Result compoundByNamePost(Http.Request request) throws Exception {
        JsonNode noderequestBody = request.body().asJson();
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
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.compoundByNamePostHttp(request, requestBody, cache);
    }

    @ApiAction
    public Result compoundByStructurePost(Http.Request request) throws Exception {
        JsonNode nodebody = request.body().asJson();
        String body;
        if (nodebody != null) {
            body = mapper.readValue(nodebody.toString(), String.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(body);
            }
        } else {
            throw new IllegalArgumentException("'body' parameter is required");
        }
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.compoundByStructurePostHttp(request, body, cache);
    }

}
