package controllers;

import apimodels.CompoundInfo;
import apimodels.CompoundList;
import apimodels.ErrorMsg;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class CompoundsApiControllerImp implements CompoundsApiControllerImpInterface {
    @Override
    public CompoundInfo compoundByIdCompoundIdGet(String compoundId) throws Exception {
        //Do your magic!!!
        return new CompoundInfo();
    }

    @Override
    public CompoundList compoundByNameNameGet(String name) throws Exception {
        //Do your magic!!!
        return new CompoundList();
    }

    @Override
    public CompoundInfo compoundByStructurePost(String body) throws Exception {
        //Do your magic!!!
        return new CompoundInfo();
    }

}
