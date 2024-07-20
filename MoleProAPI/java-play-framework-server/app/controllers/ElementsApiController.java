package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
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
public class ElementsApiController extends Controller {
    private final ElementsApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Config configuration;

    @Inject
    private ElementsApiController(Config configuration, ElementsApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }

    @ApiAction
    public Result elementByIdElementIdGet(Http.Request request, String elementId) throws Exception {
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.elementByIdElementIdGetHttp(request, elementId, cache);
    }

    @ApiAction
    public Result elementByIdPost(Http.Request request) throws Exception {
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
        return imp.elementByIdPostHttp(request, requestBody, cache);
    }

    @ApiAction
    public Result elementByNameNameGet(Http.Request request, String name) throws Exception {
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.elementByNameNameGetHttp(request, name, cache);
    }

    @ApiAction
    public Result elementByNamePost(Http.Request request) throws Exception {
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
        return imp.elementByNamePostHttp(request, requestBody, cache);
    }

}
