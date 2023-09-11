package controllers;

import apimodels.Element;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.io.FileInputStream;
import play.libs.Files.TemporaryFile;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
public class TransformersApiControllerImp extends TransformersApiControllerImpInterface {
    @Override
    public List<Element> serviceTransformPost(Http.Request request, String service, TransformerQuery transformerQuery, String cache) throws Exception {
        //Do your magic!!!
        return new ArrayList<Element>();
    }

    @Override
    public TransformerInfo serviceTransformerInfoGet(Http.Request request, String service, String cache) throws Exception {
        //Do your magic!!!
        return new TransformerInfo();
    }

}
