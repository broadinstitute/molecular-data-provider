package controllers;

import javax.inject.*;
import play.mvc.*;

public class ApiDocController extends Controller {

    @Inject
    private ApiDocController() {
    }

    public Result api() {
        return redirect("/molecular_data_provider/assets/lib/swagger-ui/index.html?url=/molecular_data_provider/assets/openapi.json");
    }
}
