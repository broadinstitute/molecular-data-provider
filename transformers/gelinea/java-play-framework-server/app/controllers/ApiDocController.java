package controllers;

import javax.inject.*;
import play.mvc.*;

public class ApiDocController extends Controller {

    @Inject
    private ApiDocController() {
    }

    public Result api() {
        return redirect("/gelinea/assets/lib/swagger-ui/index.html?url=/gelinea/assets/openapi.json");
    }
}
