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
    public Collection collectionCollectionIdGet(String collectionId) throws Exception {
        return Collections.getCollection(collectionId).asCollection();
    }

    @Override
    public CompoundList compoundListListIdGet(String listId) throws Exception {
    	return Compound.getCompoundList(listId);
    }

    @Override
    public GeneList geneListListIdGet(String listId) throws Exception {
    	return Gene.getGeneList(listId);
    }

}
