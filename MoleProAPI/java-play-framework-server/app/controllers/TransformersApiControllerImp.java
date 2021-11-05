package controllers;

import apimodels.AggregationQuery;
import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import apimodels.MoleProQuery;
import apimodels.TransformerInfo;

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
    public CollectionInfo aggregatePost(Http.Request request, AggregationQuery aggregationQuery, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public CollectionInfo transformPost(Http.Request request, MoleProQuery moleProQuery, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public List<TransformerInfo> transformersGet(Http.Request request) throws Exception {
        //Do your magic!!!
        return new ArrayList<TransformerInfo>();
    }

}
