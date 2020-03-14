package controllers;

import apimodels.AggregationQuery;
import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-03-04T17:03:22.330-05:00[America/New_York]")

public class TransformersApiControllerImp implements TransformersApiControllerImpInterface {
    @Override
    public CollectionInfo aggregatePost(AggregationQuery aggregationQuery) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public CollectionInfo transformPost(TransformerQuery transformerQuery) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public List<TransformerInfo> transformersGet() throws Exception {
        //Do your magic!!!
        return new ArrayList<TransformerInfo>();
    }

}
