package controllers;

import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import apimodels.MoleProQuery;
import apimodels.TransformerInfo;

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
public abstract class TransformersApiControllerImpInterface {
    @Inject private Config configuration;
    @Inject private SecurityAPIUtils securityAPIUtils;
    private ObjectMapper mapper = new ObjectMapper();

    public Result transformPostHttp(Http.Request request, MoleProQuery moleProQuery, String cache) throws Exception {
        CollectionInfo obj = transformPost(request, moleProQuery, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract CollectionInfo transformPost(Http.Request request, MoleProQuery moleProQuery, String cache) throws Exception;

    public Result transformersGetHttp(Http.Request request) throws Exception {
        List<TransformerInfo> obj = transformersGet(request);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            for (TransformerInfo curItem : obj) {
                OpenAPIUtils.validate(curItem);
            }
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract List<TransformerInfo> transformersGet(Http.Request request) throws Exception;

}
