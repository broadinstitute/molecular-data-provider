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
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-03-04T17:03:22.330-05:00[America/New_York]")

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
