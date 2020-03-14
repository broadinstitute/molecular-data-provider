package controllers;

import apimodels.Element;
import apimodels.ErrorMsg;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public interface TransformersApiControllerImpInterface {
    List<Element> transformPost(TransformerQuery transformerQuery) throws Exception;

    TransformerInfo transformerInfoGet() throws Exception;

}
