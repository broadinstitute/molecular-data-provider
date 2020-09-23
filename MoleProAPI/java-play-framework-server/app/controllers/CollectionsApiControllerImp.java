package controllers;

import apimodels.Collection;
import apimodels.CompoundList;
import apimodels.ErrorMsg;
import apimodels.GeneList;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class CollectionsApiControllerImp implements CollectionsApiControllerImpInterface {
    @Override
    public Collection collectionCollectionIdGet(String collectionId) throws Exception {
        //Do your magic!!!
        return new Collection();
    }

    @Override
    public CompoundList compoundListListIdGet(String listId) throws Exception {
        //Do your magic!!!
        return new CompoundList();
    }

    @Override
    public GeneList geneListListIdGet(String listId) throws Exception {
        //Do your magic!!!
        return new GeneList();
    }

}
