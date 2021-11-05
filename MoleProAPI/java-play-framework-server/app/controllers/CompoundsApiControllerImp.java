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
import java.util.LinkedHashSet;
import java.io.FileInputStream;
import play.libs.Files.TemporaryFile;
import javax.validation.constraints.*;
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
public class CompoundsApiControllerImp extends CompoundsApiControllerImpInterface {
    @Override
    public Element compoundByIdCompoundIdGet(Http.Request request, String compoundId, String cache) throws Exception {
        //Do your magic!!!
        return new Element();
    }

    @Override
    public CollectionInfo compoundByIdPost(Http.Request request, List<String> requestBody, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public Collection compoundByNameNameGet(Http.Request request, String name, String cache) throws Exception {
        //Do your magic!!!
        return new Collection();
    }

    @Override
    public CollectionInfo compoundByNamePost(Http.Request request, List<String> requestBody, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public Element compoundByStructurePost(Http.Request request, String body, String cache) throws Exception {
        //Do your magic!!!
        return new Element();
    }

}
