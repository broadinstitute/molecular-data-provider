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

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public interface TransformersApiControllerImpInterface {
    CollectionInfo aggregatePost(AggregationQuery aggregationQuery, String cache) throws Exception;

    CollectionInfo transformPost(MoleProQuery moleProQuery, String cache) throws Exception;

    List<TransformerInfo> transformersGet() throws Exception;

}
