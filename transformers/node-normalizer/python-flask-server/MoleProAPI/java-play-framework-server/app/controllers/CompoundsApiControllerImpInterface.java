package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.ErrorMsg;
import java.util.List;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public interface CompoundsApiControllerImpInterface {
    Element compoundByIdCompoundIdGet(String compoundId, String cache) throws Exception;

    CollectionInfo compoundByIdPost(List<String> requestBody, String cache) throws Exception;

    Collection compoundByNameNameGet(String name, String cache) throws Exception;

    CollectionInfo compoundByNamePost(List<String> requestBody, String cache) throws Exception;

    Element compoundByStructurePost(String body, String cache) throws Exception;

}
