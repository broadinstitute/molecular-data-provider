package controllers;

import apimodels.Collection;
import apimodels.CompoundList;
import apimodels.ErrorMsg;
import apimodels.GeneList;

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
import static play.mvc.Results.ok;
import play.libs.Files.TemporaryFile;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public abstract class CollectionsApiControllerImpInterface {
    @Inject private Config configuration;
    private ObjectMapper mapper = new ObjectMapper();

    public Result collectionCollectionIdGetHttp(Http.Request request, String collectionId, String cache) throws Exception {
        Collection obj = collectionCollectionIdGet(request, collectionId, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract Collection collectionCollectionIdGet(Http.Request request, String collectionId, String cache) throws Exception;

    public Result compoundListListIdGetHttp(Http.Request request, String listId, String cache) throws Exception {
        CompoundList obj = compoundListListIdGet(request, listId, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract CompoundList compoundListListIdGet(Http.Request request, String listId, String cache) throws Exception;

    public Result geneListListIdGetHttp(Http.Request request, String listId, String cache) throws Exception {
        GeneList obj = geneListListIdGet(request, listId, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract GeneList geneListListIdGet(Http.Request request, String listId, String cache) throws Exception;

}
