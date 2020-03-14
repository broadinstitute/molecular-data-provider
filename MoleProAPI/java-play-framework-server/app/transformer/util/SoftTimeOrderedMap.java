package transformer.util;

import java.lang.ref.SoftReference;

public class SoftTimeOrderedMap<S,T> extends TimeOrderedMap<S,SoftReference<T>> {

	private static class SoftEntry<S,T> extends Entry<S,SoftReference<T>> {

		private T value;


		SoftEntry(S key, T value) {
			super(key, new SoftReference<T>(value));
			this.value = value;
		}


		@Override
		protected void expire() {
			this.value = null;
		}


		@Override
		protected boolean isExpired() {
			return getValue() == null;
		}


		protected T getValue() {
			if (this.value != null) {
				return this.value;
			}
			return super.value.get();
		}

	}


	public SoftTimeOrderedMap(long expirationTime) {
		super(expirationTime);
	}


	public synchronized T getValue(S key) {
		final SoftEntry<S,T> entry = (SoftEntry<S,T>) getEntry(key);
		if (entry == null || entry.isExpired()) {
			return null;
		}
		return entry.getValue();
	}


	public synchronized void putValue(S key, T value) {
		final SoftEntry<S,T> entry = new SoftEntry<S,T>(key, value);
		super.put(entry);
	}


	@Override
	public synchronized void put(S key, SoftReference<T> value) {
		if (value.get() != null) {
			putValue(key, value.get());
		}
	}

}
