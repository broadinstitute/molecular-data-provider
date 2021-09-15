package transformer.util;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * A HashMap that keeps time stamps for key-value pairs and removes them after
 * they were not accessed for a certain time.
 */
public class TimeOrderedMap<S,T> implements Container<S> {

	protected static class Entry<S,T> {

		private final S key;
		protected final T value;
		private Entry<S,T> prev = null;
		private Entry<S,T> next = null;
		private long lastTime = new Date().getTime();

		private boolean expired = false;


		Entry(final S key, final T value) {
			this.value = value;
			this.key = key;
		}


		protected void expire() {
			this.expired = true;
		}


		protected boolean isExpired() {
			return expired;
		}

	}

	private final long expirationTime;

	// doubly-linked queue ordered by time
	private final Entry<S,T> head;
	private final Entry<S,T> tail;

	// underlying map
	private final Map<S,Entry<S,T>> map = new HashMap<S,Entry<S,T>>();


	/**
	 * Create a map with entries expiring after a given time
	 * 
	 * @param expirationTime
	 *            expiration time in milliseconds
	 */
	public TimeOrderedMap(final long expirationTime) {
		super();
		this.expirationTime = expirationTime;
		// set up queue
		head = new Entry<S,T>(null, null);
		tail = new Entry<S,T>(null, null);
		head.next = tail;
		tail.prev = head;
	}


	/**
	 * Returns the size of this map.
	 */
	public synchronized int size() {
		return map.size();
	}


	/**
	 * Returns true if this map contains a mapping for the specified key.
	 */
	@Override
	public synchronized boolean contains(final S key) {
		return map.containsKey(key);
	}


	/**
	 * Returns the value to which the specified key is mapped, or null if this map
	 * contains no mapping for the key.
	 */
	public synchronized T get(final S key) {
		final Entry<S,T> entry = getEntry(key);
		if (entry == null || entry.isExpired()) {
			return null;
		}
		return entry.value;
	}


	/**
	 * Associates the specified value with the specified key in this map.
	 */
	public synchronized void put(final S key, final T value) {

		final Entry<S,T> entry = new Entry<S,T>(key, value);
		this.put(entry);
	}


	/**
	 * Removes the mapping for a key from this map.
	 */
	public synchronized void remove(final S key) {
		final Entry<S,T> entry = getEntry(key);
		if (entry != null) {
			this.remove(entry);
		}
	}


	/**
	 * Returns the entry associated with the specified key, or null if this map
	 * contains no mapping for the key.
	 */
	protected synchronized Entry<S,T> getEntry(final S key) {
		final Entry<S,T> entry = map.get(key);
		if (entry == null) {
			return null;
		}
		if (entry.isExpired()) {
			this.remove(entry);
			return null;
		}
		if (entry != tail) {
			// move to the end of the queue
			entry.lastTime = new Date().getTime();
			queue_remove(entry);
			queue_append(entry);
		}
		return entry;
	}


	/**
	 * Associates the specified value with the specified key in this map.
	 */
	protected synchronized void put(final Entry<S,T> entry) {

		// remove old entry
		queue_remove(getEntry(entry.key));
		map.put(entry.key, entry);
		// put new entry to the end of the queue
		queue_append(entry);

		// expire old entries in the front of the queue
		final long now = new Date().getTime();
		Entry<S,T> e = head.next;
		while (now - e.lastTime > expirationTime && e != tail) {
			e.expire();
			e = e.next;
		}

		// traverse queue again and remove expired entries from the front of the queue
		e = head.next;
		while (now - e.lastTime > expirationTime && e != tail) {
			if (e.isExpired()) {
				remove(e);
			}
			e = e.next;
		}
	}


	/**
	 * Remove an entry from this map.
	 */
	private synchronized void remove(final Entry<S,T> entry) {
		map.remove(entry.key);
		queue_remove(entry);
	}


	// Queue operations

	/**
	 * Remove an entry from the queue.
	 */
	private void queue_remove(final Entry<S,T> entry) {
		if (entry != null) {
			entry.prev.next = entry.next;
			entry.next.prev = entry.prev;
		}
	}


	/**
	 * Append an entry to the end of the queue.
	 */
	private void queue_append(final Entry<S,T> entry) {
		entry.prev = tail.prev;
		entry.next = tail;
		tail.prev.next = entry;
		tail.prev = entry;
	}


	/**
	 * Return the size of the queue.
	 */
	synchronized int queue_size() {
		int size = 0;
		for (Entry<S,T> e = head.next; e != tail; e = e.next) {
			size = size + 1;
		}
		return size;
	}
}
