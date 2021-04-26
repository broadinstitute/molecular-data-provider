package transformer.util;

import java.lang.ref.SoftReference;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public abstract class Cache<S,K,V> {

	private final Map<S,SoftTimeOrderedMap<K,V>> map = new HashMap<>();

	private final long expirationTime;


	public Cache(long expirationTime) {
		super();
		this.expirationTime = expirationTime;
	}


	public synchronized void addKeySet(S keySet) {
		if (!map.containsKey(keySet)) {
			map.put(keySet, new SoftTimeOrderedMap<K,V>(expirationTime));
		}
	}


	public synchronized void save(V value) {
		SoftReference<V> reference = new SoftReference<>(value);
		for (KeyPair<S,K> keyPair : getKeys(value)) {
			if (keyPair.keySet != null && keyPair.key != null) {
				map.get(keyPair.keySet).put(keyPair.key, reference);
			}
		}
	}


	public synchronized V get(S keySet, K key) {
		if (map.containsKey(keySet) && map.get(keySet).contains(key) && map.get(keySet).get(key) != null) {
			return map.get(keySet).get(key).get();
		}
		return null;
	}


	public synchronized void put(S keySet, K key, V value) {
		SoftReference<V> reference = new SoftReference<>(value);
		map.get(keySet).put(key, reference);
	}


	public synchronized int size() {
		int size = 0;
		for (SoftTimeOrderedMap<K,V> map: map.values()) {
			size = Math.max(size, map.size());
		}
		return size;
	}


	protected abstract List<KeyPair<S,K>> getKeys(V value);


	protected static class KeyPair<S,K> {
		public final S keySet;
		public final K key;


		public KeyPair(S keySet, K key) {
			super();
			this.keySet = keySet;
			this.key = key;
		}
	}
}
