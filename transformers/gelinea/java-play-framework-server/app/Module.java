import com.google.inject.AbstractModule;

import controllers.*;
import openapitools.SecurityAPIUtils;

public class Module extends AbstractModule {

    @Override
    protected void configure() {
        bind(TransformersApiControllerImpInterface.class).to(TransformersApiControllerImp.class);
        bind(SecurityAPIUtils.class);
    }
}