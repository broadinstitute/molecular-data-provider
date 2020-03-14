package controllers;

import apimodels.Collection;
import apimodels.CompoundList;
import apimodels.ErrorMsg;
import apimodels.GeneList;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public interface CollectionsApiControllerImpInterface {
    Collection collectionCollectionIdGet(String collectionId) throws Exception;

    CompoundList compoundListListIdGet(String listId) throws Exception;

    GeneList geneListListIdGet(String listId) throws Exception;

}
