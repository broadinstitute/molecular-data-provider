package controllers;

import apimodels.ChainQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import java.util.List;
import apimodels.MoleProQuery;
import apimodels.TransformerInfo;

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
    public Result transformChainPost(Http.Request request) throws Exception {
        JsonNode nodechainQuery = request.body().asJson();
        List<ChainQuery> chainQuery;
        if (nodechainQuery != null) {
            chainQuery = mapper.readValue(nodechainQuery.toString(), new TypeReference<List<ChainQuery>>(){});
            if (configuration.getBoolean("useInputBeanValidation")) {
                for (ChainQuery curItem : chainQuery) {
                    OpenAPIUtils.validate(curItem);
                }
            }
        } else {
            throw new IllegalArgumentException("'ChainQuery' parameter is required");
        }
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.transformChainPostHttp(request, chainQuery, cache);
    }

    @ApiAction
    public Result transformPost(Http.Request request) throws Exception {
        JsonNode nodemoleProQuery = request.body().asJson();
        MoleProQuery moleProQuery;
        if (nodemoleProQuery != null) {
            moleProQuery = mapper.readValue(nodemoleProQuery.toString(), MoleProQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(moleProQuery);
            }
        } else {
            throw new IllegalArgumentException("'MoleProQuery' parameter is required");
        }
        String valuecache = request.getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        return imp.transformPostHttp(request, moleProQuery, cache);
    }

    @ApiAction
    public Result transformersGet(Http.Request request) throws Exception {
        return imp.transformersGetHttp(request);
    }

}
