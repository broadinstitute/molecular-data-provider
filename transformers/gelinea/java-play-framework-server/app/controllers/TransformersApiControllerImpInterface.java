package controllers;

import apimodels.Element;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

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

    public Result serviceTransformPostHttp(Http.Request request, String service, TransformerQuery transformerQuery, String cache) throws Exception {
        List<Element> obj = serviceTransformPost(request, service, transformerQuery, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            for (Element curItem : obj) {
                OpenAPIUtils.validate(curItem);
            }
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract List<Element> serviceTransformPost(Http.Request request, String service, TransformerQuery transformerQuery, String cache) throws Exception;

    public Result serviceTransformerInfoGetHttp(Http.Request request, String service, String cache) throws Exception {
        TransformerInfo obj = serviceTransformerInfoGet(request, service, cache);

        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }

        JsonNode result = mapper.valueToTree(obj);

        return ok(result);

    }

    public abstract TransformerInfo serviceTransformerInfoGet(Http.Request request, String service, String cache) throws Exception;

}
