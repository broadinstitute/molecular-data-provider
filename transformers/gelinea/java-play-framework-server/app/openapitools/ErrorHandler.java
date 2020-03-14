package openapitools;


import play.*;
import play.api.OptionalSourceMapper;
import play.api.UsefulException;
import play.api.routing.Router;
import play.http.DefaultHttpErrorHandler;
import play.mvc.Http.*;
import play.mvc.*;

import javax.inject.*;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import apimodels.ErrorMsg;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import static play.mvc.Results.*;

@Singleton
public class ErrorHandler extends DefaultHttpErrorHandler {

    final static Logger log = LoggerFactory.getLogger("application");
    
    private final ObjectMapper mapper;
    
    @Inject
    public ErrorHandler(Configuration configuration, Environment environment, OptionalSourceMapper sourceMapper, Provider<Router> routes) {
        super(configuration, environment, sourceMapper, routes);
        mapper = new ObjectMapper();
    }

    @Override
    protected CompletionStage<Result> onDevServerError(RequestHeader request, UsefulException exception) {
        return CompletableFuture.completedFuture(
            handleExceptions(exception)
        );
    }

    @Override
    protected CompletionStage<Result> onProdServerError(RequestHeader request, UsefulException exception) {
        return CompletableFuture.completedFuture(
            handleExceptions(exception)
        );
    }

    @Override
    protected void logServerError(RequestHeader request, UsefulException usefulException) {
        //Since the error is already handled, we don't want to print anything on the console
        //But if you want to have the error printed in the console, just delete this override
    }

    private Result handleExceptions(Throwable t) {
    	Throwable cause = (t.getCause() != null) ? t.getCause() : t;
        log.warn(cause.getMessage(), cause);
        return internalServerError(errorMsg(cause, 500, "Internal Server Error"));
    }

    private JsonNode errorMsg(Throwable cause, int status, String title) {
        ErrorMsg msg = new ErrorMsg().status(status).title(title).detail(cause.getMessage()).type("about:blank");
        return mapper.valueToTree(msg);
    }
}
