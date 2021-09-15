package transformer.collection;

import scala.util.Random;
import transformer.util.Container;

public class IdGenerator {

	private final int idLength;
	
	private final Container<String> container;
	
	public IdGenerator(int idLength, Container<String> container) {
		this.idLength = idLength;
		this.container = container;
	}
	
	public synchronized String nextId() {
		String id = randString(idLength);
		while (container.contains(id)) {
			id = randString(idLength);
		}
		return id;
	}
	
	// STATIC
	
	private static Random rand = new Random();


	private static String randString(int len) {
		return rand.alphanumeric().take(len).mkString();
	}

}
