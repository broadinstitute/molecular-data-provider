package controllers;

import apimodels.CompoundInfo;
import apimodels.CompoundList;
import apimodels.ErrorMsg;

import play.mvc.Http;
import transformer.classes.Compound;

import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.FileInputStream;
import javax.validation.constraints.*;

public class CompoundsApiControllerImp implements CompoundsApiControllerImpInterface {
    @Override
    public CompoundInfo compoundByIdCompoundIdGet(String compoundId) throws Exception {
        return Compound.getCompoundById(compoundId);
    }

    @Override
    public CompoundList compoundByNameNameGet(String name) throws Exception {
        return Compound.getCompoundByName(name);
    }

    @Override
    public CompoundInfo compoundByStructurePost(String body) throws Exception {
        return Compound.getCompoundByStructure(body);
    }

}
