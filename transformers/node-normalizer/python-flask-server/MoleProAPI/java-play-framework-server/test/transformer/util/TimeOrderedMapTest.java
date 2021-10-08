package transformer.util;

import org.junit.Test;
import static org.junit.Assert.*;

public class TimeOrderedMapTest {

	@Test
	public void testPut() throws Exception {
		TimeOrderedMap<String,String> map = new TimeOrderedMap<>(2000);
		assertNull(map.get("test"));
		assertEquals(map.size(), 0);
		assertEquals(map.queue_size(), 0);

		map.put("test", "test");
		assertEquals(map.get("test"), "test");
		assertEquals(map.size(), 1);
		assertEquals(map.queue_size(), 1);
		map.put("test", "test");
		assertEquals(map.get("test"), "test");
		assertEquals(map.size(), 1);
		assertEquals(map.queue_size(), 1);
		map.put("new", "new");
		assertEquals(map.get("new"), "new");
		assertEquals(map.size(), 2);
		assertEquals(map.queue_size(), 2);
	}


	@Test
	public void testExpire() throws Exception {
		TimeOrderedMap<String,String> map = new TimeOrderedMap<>(2000);
		assertNull(map.get("test"));
		assertEquals(map.size(), 0);
		assertEquals(map.queue_size(), 0);

		map.put("test", "test");
		assertEquals(map.get("test"), "test");
		assertEquals(map.size(), 1);
		assertEquals(map.queue_size(), 1);

		Thread.sleep(2500);
		map.put("new", "new");
		assertNull(map.get("test"));
		assertEquals(map.size(), 1);
		assertEquals(map.queue_size(), 1);
	}

}
