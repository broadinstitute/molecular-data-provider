import com.google.inject.AbstractModule;

import controllers.*;
import openapitools.SecurityAPIUtils;

public class Module extends AbstractModule {

    @Override
    protected void configure() {
        bind(CollectionsApiControllerImpInterface.class).to(CollectionsApiControllerImp.class);
        bind(CompoundsApiControllerImpInterface.class).to(CompoundsApiControllerImp.class);
        bind(ElementsApiControllerImpInterface.class).to(ElementsApiControllerImp.class);
        bind(TransformersApiControllerImpInterface.class).to(TransformersApiControllerImp.class);
        bind(SecurityAPIUtils.class);
    }
}