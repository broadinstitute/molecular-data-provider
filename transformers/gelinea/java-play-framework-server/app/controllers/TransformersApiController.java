package controllers;

import apimodels.Element;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-02-27T16:03:08.782-05:00[America/New_York]")

public class TransformersApiController extends Controller {

    private final TransformersApiControllerImpInterface imp;
    private final ObjectMapper mapper;
    private final Configuration configuration;

    @Inject
    private TransformersApiController(Configuration configuration, TransformersApiControllerImpInterface imp) {
        this.imp = imp;
        mapper = new ObjectMapper();
        this.configuration = configuration;
    }


    @ApiAction
    public Result transformPost() throws Exception {
        JsonNode nodetransformerQuery = request().body().asJson();
        TransformerQuery transformerQuery;
        if (nodetransformerQuery != null) {
            transformerQuery = mapper.readValue(nodetransformerQuery.toString(), TransformerQuery.class);
            if (configuration.getBoolean("useInputBeanValidation")) {
                OpenAPIUtils.validate(transformerQuery);
            }
        } else {
            throw new IllegalArgumentException("'TransformerQuery' parameter is required");
        }
        List<Element> obj = imp.transformPost(transformerQuery);
        if (configuration.getBoolean("useOutputBeanValidation")) {
            for (Element curItem : obj) {
                OpenAPIUtils.validate(curItem);
            }
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }

    @ApiAction
    public Result transformerInfoGet() throws Exception {
        TransformerInfo obj = imp.transformerInfoGet();
        if (configuration.getBoolean("useOutputBeanValidation")) {
            OpenAPIUtils.validate(obj);
        }
        JsonNode result = mapper.valueToTree(obj);
        return ok(result);
    }
}
