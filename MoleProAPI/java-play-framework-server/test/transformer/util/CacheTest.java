package transformer.util;

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.List;

import org.junit.Test;

public class CacheTest {

	private Cache<String,String,TestValue> cache = new Cache<String,String,TestValue>(2000) {

		@Override
		protected List<KeyPair<String,String>> getKeys(TestValue value) {
			List<KeyPair<String,String>> keys = new ArrayList<>();
			keys.add(new KeyPair<String,String>("A", value.idA));
			keys.add(new KeyPair<String,String>("B", value.idB1));
			keys.add(new KeyPair<String,String>("B", value.idB2));

			return keys;
		}

	};


	@Test
	public void testCache() throws Exception {
		cache.addKeySet("A");
		cache.addKeySet("B");

		TestValue valueABC = new TestValue("a", "b", "c", "ABC");
		TestValue valueXYZ = new TestValue("x", "y", "z", "XYZ");
		cache.save(valueABC);
		cache.save(valueXYZ);

		assertEquals("ABC", cache.get("A", "a").value);
		assertEquals("ABC", cache.get("B", "b").value);
		assertEquals("ABC", cache.get("B", "c").value);
		assertEquals("XYZ", cache.get("A", "x").value);
		assertEquals("XYZ", cache.get("B", "y").value);
		assertEquals("XYZ", cache.get("B", "y").value);

		Thread.sleep(2500);
		assertEquals("ABC", cache.get("A", "a").value);
		assertEquals("ABC", cache.get("B", "b").value);
		assertEquals("ABC", cache.get("B", "c").value);
		assertEquals("XYZ", cache.get("A", "x").value);
		assertEquals("XYZ", cache.get("B", "y").value);
		assertEquals("XYZ", cache.get("B", "y").value);
	}


	static class TestValue {

		String idA;
		String idB1;
		String idB2;

		String value;


		protected TestValue(String idA, String idB1, String idB2, String value) {
			super();
			this.idA = idA;
			this.idB1 = idB1;
			this.idB2 = idB2;
			this.value = value;
		}

	}
}
