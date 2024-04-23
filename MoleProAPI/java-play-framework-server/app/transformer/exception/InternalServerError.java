package transformer.exception;

@SuppressWarnings("serial")
public class InternalServerError extends Error {

	public InternalServerError(String message) {
		super(message);
	}


	public InternalServerError(String message, Throwable cause) {
		super(message, cause);
	}
}
