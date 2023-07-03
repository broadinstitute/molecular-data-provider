package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.ErrorMsg;
import java.util.List;

import play.mvc.Http;
import transformer.elements.Elements;

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
        return Elements.getCompoundById(compoundId, cache);
    }

    @Override
    public CollectionInfo compoundByIdPost(Http.Request request, List<String> requestBody, String cache) throws Exception {
    	return Elements.getCompoundsById(requestBody, cache);
    }

    @Override
    public Collection compoundByNameNameGet(Http.Request request, String name, String cache) throws Exception {
        return Elements.getCompoundByName(name, cache);
    }

    @Override
    public CollectionInfo compoundByNamePost(Http.Request request, List<String> requestBody, String cache) throws Exception {
    	return Elements.getCompoundsByName(requestBody, cache);
    }

    @Override
    public Element compoundByStructurePost(Http.Request request, String body, String cache) throws Exception {
        return Elements.getCompoundByStructure(body, cache);
    }

}
