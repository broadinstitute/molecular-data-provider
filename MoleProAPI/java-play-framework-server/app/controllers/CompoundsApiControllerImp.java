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
import java.util.LinkedHashSet;
import java.io.FileInputStream;
import play.libs.Files.TemporaryFile;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
public class CompoundsApiControllerImp extends CompoundsApiControllerImpInterface {
    @Override

    public Element compoundByIdCompoundIdGet(Http.Request request, String compoundId, String cache) throws Exception {
        return Compound.getCompoundById(compoundId);
    }

    @Override
    public CollectionInfo compoundByIdPost(Http.Request request, List<String> requestBody, String cache) throws Exception {
    	return Compound.getCompoundsById(requestBody, cache);
    }

    @Override
    public Collection compoundByNameNameGet(Http.Request request, String name, String cache) throws Exception {
        return Compound.getCompoundByName(name, cache);
    }

    @Override
    public CollectionInfo compoundByNamePost(Http.Request request, List<String> requestBody, String cache) throws Exception {
    	return Compound.getCompoundsByName(requestBody, cache);
    }

    @Override
    public Element compoundByStructurePost(Http.Request request, String body, String cache) throws Exception {
        return Compound.getCompoundByStructure(body);
    }

}
