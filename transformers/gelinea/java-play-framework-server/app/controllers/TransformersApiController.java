package controllers;

import apimodels.Element;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

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
public class TransformersApiController extends Controller {
    private final TransformersApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Config configuration;

    @Inject
    private TransformersApiController(Config configuration, TransformersApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }

    @ApiAction
    public Result serviceTransformPost(Http.Request request, String service) throws Exception {
        JsonNode nodetransformerQuery = request.body().asJson();
        TransformerQuery transformerQuery;
        if (nodetransformerQuery != null) {
            transformerQuery = mapper.readValue(nodetransformerQuery.toString(), TransformerQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(transformerQuery);
            }
        } else {
            throw new IllegalArgumentException("'TransformerQuery' parameter is required");
        }
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.serviceTransformPostHttp(request, service, transformerQuery, cache);
    }

    @ApiAction
    public Result serviceTransformerInfoGet(Http.Request request, String service) throws Exception {
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.serviceTransformerInfoGetHttp(request, service, cache);
    }

}
