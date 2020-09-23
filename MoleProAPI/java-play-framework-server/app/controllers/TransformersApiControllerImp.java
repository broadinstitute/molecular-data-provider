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
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class TransformersApiControllerImp implements TransformersApiControllerImpInterface {
    @Override
    public CollectionInfo aggregatePost(AggregationQuery aggregationQuery) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public CollectionInfo transformPost(MoleProQuery moleProQuery) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public List<TransformerInfo> transformersGet() throws Exception {
        //Do your magic!!!
        return new ArrayList<TransformerInfo>();
    }

}
