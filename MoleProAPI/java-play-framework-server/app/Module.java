import com.google.inject.AbstractModule;

import controllers.*;

public class Module extends AbstractModule {

    @Override
    protected void configure() {
        bind(CollectionsApiControllerImpInterface.class).to(CollectionsApiControllerImp.class);
        bind(CompoundsApiControllerImpInterface.class).to(CompoundsApiControllerImp.class);
        bind(TransformersApiControllerImpInterface.class).to(TransformersApiControllerImp.class);
    }
}