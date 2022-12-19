package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.ErrorMsg;
import java.util.List;

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
public abstract class CompoundsApiControllerImpInterface {
    @Inject private Config configuration;
    private ObjectMapper mapper = new ObjectMapper();

    public Result compoundByIdCompoundIdGetHttp(Http.Request request, String compoundId, String cache) throws Exception {
        Element obj = compoundByIdCompoundIdGet(request, compoundId, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract Element compoundByIdCompoundIdGet(Http.Request request, String compoundId, String cache) throws Exception;

    public Result compoundByIdPostHttp(Http.Request request, List<String> requestBody, String cache) throws Exception {
        CollectionInfo obj = compoundByIdPost(request, requestBody, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract CollectionInfo compoundByIdPost(Http.Request request, List<String> requestBody, String cache) throws Exception;

    public Result compoundByNameNameGetHttp(Http.Request request, String name, String cache) throws Exception {
        Collection obj = compoundByNameNameGet(request, name, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract Collection compoundByNameNameGet(Http.Request request, String name, String cache) throws Exception;

    public Result compoundByNamePostHttp(Http.Request request, List<String> requestBody, String cache) throws Exception {
        CollectionInfo obj = compoundByNamePost(request, requestBody, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract CollectionInfo compoundByNamePost(Http.Request request, List<String> requestBody, String cache) throws Exception;

    public Result compoundByStructurePostHttp(Http.Request request, String body, String cache) throws Exception {
        Element obj = compoundByStructurePost(request, body, cache);
    if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
    }
JsonNode result = mapper.valueToTree(obj);
return ok(result);

    }

    public abstract Element compoundByStructurePost(Http.Request request, String body, String cache) throws Exception;

}
