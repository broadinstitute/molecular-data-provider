package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
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
import openapitools.SecurityAPIUtils;
import static play.mvc.Results.ok;
import static play.mvc.Results.unauthorized;
import play.libs.Files.TemporaryFile;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public abstract class ElementsApiControllerImpInterface {
    @Inject private Config configuration;
    @Inject private SecurityAPIUtils securityAPIUtils;
    private ObjectMapper mapper = new ObjectMapper();

    public Result elementByIdCompoundIdGetHttp(Http.Request request, String compoundId, String cache) throws Exception {
        Collection obj = elementByIdCompoundIdGet(request, compoundId, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract Collection elementByIdCompoundIdGet(Http.Request request, String compoundId, String cache) throws Exception;

    public Result elementByIdPostHttp(Http.Request request, List<String> requestBody, String cache) throws Exception {
        CollectionInfo obj = elementByIdPost(request, requestBody, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract CollectionInfo elementByIdPost(Http.Request request, List<String> requestBody, String cache) throws Exception;

    public Result elementByNameNameGetHttp(Http.Request request, String name, String cache) throws Exception {
        Collection obj = elementByNameNameGet(request, name, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract Collection elementByNameNameGet(Http.Request request, String name, String cache) throws Exception;

    public Result elementByNamePostHttp(Http.Request request, List<String> requestBody, String cache) throws Exception {
        CollectionInfo obj = elementByNamePost(request, requestBody, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract CollectionInfo elementByNamePost(Http.Request request, List<String> requestBody, String cache) throws Exception;

}
