package controllers;

import apimodels.AggregationQuery;
import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import apimodels.MoleProQuery;
import apimodels.TransformerInfo;

import play.mvc.Http;
import transformer.Transformers;
import transformer.collection.Aggregator;

import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class TransformersApiControllerImp implements TransformersApiControllerImpInterface {
    @Override
    public CollectionInfo aggregatePost(AggregationQuery aggregationQuery, String cache) throws Exception {
        return Aggregator.aggregate(aggregationQuery, cache);
    }

    @Override
    public CollectionInfo transformPost(MoleProQuery moleProQuery, String cache) throws Exception {
        return Transformers.getTransformer(moleProQuery.getName()).transform(moleProQuery, cache);
    }

    @Override
    public List<TransformerInfo> transformersGet() throws Exception {
        return Transformers.getTransformers();
    }

}
