package controllers;

import apimodels.CompoundInfo;
import apimodels.CompoundList;
import apimodels.ErrorMsg;

import play.mvc.Http;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

import javax.validation.constraints.*;

@SuppressWarnings("RedundantThrows")
public interface CompoundsApiControllerImpInterface {
    CompoundInfo compoundByIdCompoundIdGet(String compoundId) throws Exception;

    CompoundList compoundByNameNameGet(String name) throws Exception;

    CompoundInfo compoundByStructurePost(String body) throws Exception;

}
