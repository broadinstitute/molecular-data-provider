package transformer.collection;

import apimodels.CollectionInfo;
import transformer.Config;
import transformer.exception.NotFoundException;
import transformer.util.TimeOrderedMap;

public class Collections {

	public static interface CACHE {
		public static String YES = "yes";
		public static String NO = "no";
	}

	private static long EXPIRATION = Config.config.getExpirationTimes().getCollections();
	
	private static TimeOrderedMap<String,CollectionsEntry> collections = new TimeOrderedMap<String,CollectionsEntry>(EXPIRATION);

	private static IdGenerator idGenerator = new IdGenerator(10, collections);


	public synchronized static CollectionsEntry getCollection(String collectionId, String cache) throws NotFoundException {
		CollectionsEntry collection = collections.get(collectionId);
		if (collection == null) {
			throw new NotFoundException("Collection " + collectionId + " not found");
		}
		if (cache(cache).equals(CACHE.NO)) {
			collections.remove(collectionId);
		}
		return collection;
	}


	public synchronized static void save(CollectionsEntry collection) {
		save(collection, CACHE.YES);
	}


	public synchronized static void save(CollectionsEntry collection, String cache) {
		String id = idGenerator.nextId();
		CollectionInfo info = collection.getInfo();
		info.setId(id);
		String url = info.getUrl();
		if (url == null) {
			url = Config.config.url().getBaseURL() + "/collection/";
		}
		url = url + id;
		info.setUrl(url);

		if (!cache(cache).equals(CACHE.NO)) {
			collections.put(id, collection);
		}
	}


	private static String cache(String cache) {
		if (cache == null || cache.equals("")) {
			return CACHE.YES;
		}
		return cache.toLowerCase();
	}


	public static int size() {
		return collections.size();
	}
}
