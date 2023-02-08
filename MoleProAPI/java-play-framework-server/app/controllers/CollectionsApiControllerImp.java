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
import java.util.LinkedHashSet;
import java.io.FileInputStream;
import play.libs.Files.TemporaryFile;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
public class CollectionsApiControllerImp extends CollectionsApiControllerImpInterface {
    @Override
    public Collection collectionCollectionIdGet(Http.Request request, String collectionId, String cache) throws Exception {
        return Collections.getCollection(collectionId, cache).asCollection();
    }

    @Override
    public CompoundList compoundListListIdGet(Http.Request request, String listId, String cache) throws Exception {
        return Compound.getCompoundList(listId, cache);
    }

    @Override
    public GeneList geneListListIdGet(Http.Request request, String listId, String cache) throws Exception {
        return Gene.getGeneList(listId, cache);
    }

}
