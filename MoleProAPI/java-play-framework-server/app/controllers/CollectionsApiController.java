package controllers;

import apimodels.Collection;
import apimodels.CompoundList;
import apimodels.ErrorMsg;
import apimodels.GeneList;

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


public class CollectionsApiController extends Controller {

    private final CollectionsApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Configuration configuration;

    @Inject
    private CollectionsApiController(Configuration configuration, CollectionsApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }


    @ApiAction
    public Result collectionCollectionIdGet(String collectionId) throws Exception {
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        Collection obj = imp.collectionCollectionIdGet(collectionId, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result compoundListListIdGet(String listId) throws Exception {
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        CompoundList obj = imp.compoundListListIdGet(listId, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result geneListListIdGet(String listId) throws Exception {
        String valuecache = request().getQueryString("cache");
        String cache;
        if (valuecache != null) {
            cache = valuecache;
        } else {
            cache = null;
        }
        GeneList obj = imp.geneListListIdGet(listId, cache);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }
}
