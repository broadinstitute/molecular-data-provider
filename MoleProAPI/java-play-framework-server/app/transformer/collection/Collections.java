package transformer.collection;

import apimodels.CollectionInfo;
import transformer.Config;
import transformer.exception.NotFoundException;
import transformer.util.TimeOrderedMap;

public class Collections {

	private static long TWO_WEEKS = 14 * 24 * 60 * 60 * 1000/* two weeks */;

	private static TimeOrderedMap<String,CollectionsEntry> collections = new TimeOrderedMap<String,CollectionsEntry>(TWO_WEEKS);

	private static IdGenerator idGenerator = new IdGenerator(10, collections);


	public synchronized static CollectionsEntry getCollection(String collectionId) throws NotFoundException {
		CollectionsEntry collection = collections.get(collectionId);
		if (collection == null) {
			throw new NotFoundException("Collection " + collectionId + " not found");
		}
		return collection;
	}


	public synchronized static void save(CollectionsEntry collection) {
		String id = idGenerator.nextId();
		CollectionInfo info = collection.getInfo();
		info.setId(id);
		String url = info.getUrl();
		if (url == null) {
			url = Config.config.url().getBaseURL()+"/"+info.getElementClass()+"/list/";
		}
		url = url +id;
		info.setUrl(url);
		collections.put(id, collection);
	}
}
