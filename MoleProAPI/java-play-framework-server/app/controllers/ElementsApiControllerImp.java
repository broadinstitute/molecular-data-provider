package controllers;

import apimodels.Collection;
import apimodels.CollectionInfo;
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
public class ElementsApiControllerImp extends ElementsApiControllerImpInterface {
    @Override
    public Collection elementByIdElementIdGet(Http.Request request, String elementId, String cache) throws Exception {
        return Elements.elementById(elementId, cache);
    }

    @Override
    public CollectionInfo elementByIdPost(Http.Request request, List<String> requestBody, String cache) throws Exception {
        return Elements.elementById(requestBody, cache);
    }

    @Override
    public Collection elementByNameNameGet(Http.Request request, String name, String cache) throws Exception {
    	return Elements.elementByName(name, cache);
    }

    @Override
    public CollectionInfo elementByNamePost(Http.Request request, List<String> requestBody, String cache) throws Exception {
    	return Elements.elementByName(requestBody, cache);
    }

}
