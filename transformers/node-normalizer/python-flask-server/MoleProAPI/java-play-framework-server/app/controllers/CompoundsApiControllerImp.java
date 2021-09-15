package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.ErrorMsg;
import java.util.List;

import play.mvc.Http;
import transformer.classes.Compound;

import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class CompoundsApiControllerImp implements CompoundsApiControllerImpInterface {
    @Override
    public Element compoundByIdCompoundIdGet(String compoundId, String cache) throws Exception {
        return Compound.getCompoundById(compoundId);
    }

    @Override
    public CollectionInfo compoundByIdPost(List<String> requestBody, String cache) throws Exception {
    	return Compound.getCompoundsById(requestBody, cache);
    }

    @Override
    public Collection compoundByNameNameGet(String name, String cache) throws Exception {
        return Compound.getCompoundByName(name, cache);
    }

    @Override
    public CollectionInfo compoundByNamePost(List<String> requestBody, String cache) throws Exception {
    	return Compound.getCompoundsByName(requestBody, cache);
    }

    @Override
    public Element compoundByStructurePost(String body, String cache) throws Exception {
        return Compound.getCompoundByStructure(body);
    }

}
