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
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class CompoundsApiControllerImp implements CompoundsApiControllerImpInterface {
    @Override
    public Element compoundByIdCompoundIdGet(String compoundId, String cache) throws Exception {
        //Do your magic!!!
        return new Element();
    }

    @Override
    public CollectionInfo compoundByIdPost(List<String> requestBody, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public Collection compoundByNameNameGet(String name, String cache) throws Exception {
        //Do your magic!!!
        return new Collection();
    }

    @Override
    public CollectionInfo compoundByNamePost(List<String> requestBody, String cache) throws Exception {
        //Do your magic!!!
        return new CollectionInfo();
    }

    @Override
    public Element compoundByStructurePost(String body, String cache) throws Exception {
        //Do your magic!!!
        return new Element();
    }

}
