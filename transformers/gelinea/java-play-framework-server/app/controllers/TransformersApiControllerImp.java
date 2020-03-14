package controllers;

import apimodels.Element;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;
import gelinea.GeLiNEATransformer;
import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-02-27T16:03:08.782-05:00[America/New_York]")

public class TransformersApiControllerImp implements TransformersApiControllerImpInterface {

    GeLiNEATransformer transformer = new GeLiNEATransformer();

    @Override
    public List<Element> transformPost(TransformerQuery transformerQuery) throws Exception {
        return transformer.transform(transformerQuery);
    }

    @Override
    public TransformerInfo transformerInfoGet() throws Exception {
        return transformer.getInfo();
    }

}
