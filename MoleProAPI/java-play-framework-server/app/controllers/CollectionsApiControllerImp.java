package controllers;

import apimodels.Collection;
import apimodels.CompoundList;
import apimodels.ErrorMsg;
import apimodels.GeneList;

import play.mvc.Http;
import transformer.classes.Compound;
import transformer.classes.Gene;
import transformer.collection.Collections;

import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class CollectionsApiControllerImp implements CollectionsApiControllerImpInterface {
    @Override
    public Collection collectionCollectionIdGet(String collectionId, String cache) throws Exception {
        return Collections.getCollection(collectionId, cache).asCollection();
    }

    @Override
    public CompoundList compoundListListIdGet(String listId, String cache) throws Exception {
    	return Compound.getCompoundList(listId, cache);
    }

    @Override
    public GeneList geneListListIdGet(String listId, String cache) throws Exception {
    	return Gene.getGeneList(listId, cache);
    }

}
