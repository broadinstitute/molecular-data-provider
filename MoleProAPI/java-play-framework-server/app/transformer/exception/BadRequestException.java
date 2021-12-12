package transformer.exception;

@SuppressWarnings("serial")
public class BadRequestException extends Exception {

	public BadRequestException(String message) {
		super(message);
	}

}
