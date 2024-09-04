package controllers;

import apimodels.ChainQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.ErrorMsg;
import java.util.List;
import apimodels.MoleProQuery;
import apimodels.TransformerInfo;

import play.mvc.Http;
import transformer.Transformers;
import transformer.collection.Aggregator;

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
    public Collection transformChainPost(Http.Request request, List<ChainQuery> chainQuery, String cache) throws Exception {
        return Transformers.getChainTransformer(chainQuery).transform(cache);
    }

    @Override
    public CollectionInfo transformPost(Http.Request request, MoleProQuery moleProQuery, String cache) throws Exception {
        return Transformers.getTransformer(moleProQuery.getName()).transform(moleProQuery, cache);
    }

    @Override
    public List<TransformerInfo> transformersGet(Http.Request request) throws Exception {
        return Transformers.getTransformers();
    }

}
