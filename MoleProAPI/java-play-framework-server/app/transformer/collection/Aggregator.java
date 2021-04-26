package transformer.collection;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

import apimodels.AggregationQuery;
import apimodels.Attribute;
import apimodels.CollectionInfo;
import transformer.exception.BadRequestException;

public class Aggregator {

	public static CollectionInfo aggregate(final AggregationQuery query, String cache) throws Exception {
		final String operation = query.getOperation();
		final List<CollectionsEntry> collections = getCollections(query.getCollectionIds(), cache);
		CollectionsEntry aggregate = aggregate(operation, collections);
		aggregate.getInfo().setSource(operation);
		Collections.save(aggregate);
		return aggregate.getInfo();
	}


	public static CollectionsEntry aggregate(final String operation, final List<CollectionsEntry> collections) throws Exception {
		if (operation.equals("union")) {
			return union(collections);
		}
		else if (operation.equals("intersection")) {
			return intersection(collections);
		}
		else if (operation.equals("difference")) {
			return difference(collections);
		}
		else if (operation.equals("symmetric difference")) {
			return symDifference(collections);
		}
		else {
			throw new BadRequestException("Unknown aggregation operation: " + operation);
		}
	}


	private static List<CollectionsEntry> getCollections(final List<String> collectionIds, String cache) throws Exception {
		if (collectionIds == null || collectionIds.size() == 0) {
			throw new BadRequestException("Empty collection list");
		}
		final List<CollectionsEntry> collections = new ArrayList<>(collectionIds.size());
		String collectionClass = null;
		for (String id : collectionIds) {
			CollectionsEntry collection = Collections.getCollection(id, cache);
			if (collectionClass == null) {
				collectionClass = collection.getInfo().getElementClass();
			}
			else if (!collectionClass.equals(collection.getInfo().getElementClass())) {
				throw new BadRequestException("Aggregation collections must have elements of the same class");
			}
			collections.add(collection);
		}
		return collections;
	}


	public static CollectionsEntry union(final List<CollectionsEntry> collections) {
		final CollectionInfo info = new CollectionInfo().attributes(new ArrayList<Attribute>());
		final HashMap<String,CollectionElement> elements = new HashMap<>();
		final List<CollectionElement> union = new ArrayList<>();
		for (CollectionsEntry collection : collections) {
			info.setElementClass(collection.getInfo().getElementClass());
			for (CollectionElement element : collection.getElements()) {
				if (!elements.containsKey(element.getId())) {
					final CollectionElement unionElement = element.duplicate();
					union.add(unionElement);
					elements.put(element.getId(), unionElement);
				}
				elements.get(element.getId()).merge(element);
			}
		}
		return CollectionsEntry.create(info, union);
	}


	private static CollectionsEntry intersection(final List<CollectionsEntry> collections) {
		final CollectionInfo info = new CollectionInfo().attributes(new ArrayList<Attribute>());
		HashMap<String,CollectionElement> intersection = new HashMap<>();
		for (CollectionElement element : collections.get(0).getElements()) {
			intersection.put(element.getId(), element.duplicate());
		}
		for (CollectionsEntry collection : collections) {
			info.setElementClass(collection.getInfo().getElementClass());
			final HashMap<String,CollectionElement> newIntersection = new HashMap<>();
			for (CollectionElement element : collection.getElements()) {
				final String id = element.getId();
				if (intersection.containsKey(id)) {
					newIntersection.put(id, intersection.get(id));
					newIntersection.get(id).merge(element);
				}
			}
			intersection = newIntersection;
		}
		return CollectionsEntry.create(info, intersection(collections.get(0), intersection));
	}


	private static List<CollectionElement> intersection(CollectionsEntry source, HashMap<String,CollectionElement> elements) {
		final List<CollectionElement> intersection = new ArrayList<>();
		for (CollectionElement element : source.getElements()) {
			if (elements.containsKey(element.getId())) {
				intersection.add(elements.get(element.getId()));
			}
		}
		return intersection;
	}


	private static CollectionsEntry symDifference(final List<CollectionsEntry> collections) {
		final HashSet<String> intersection = new HashSet<String>();
		for (CollectionElement element : intersection(collections).getElements()) {
			intersection.add(element.getId());
		}
		final CollectionInfo info = new CollectionInfo().attributes(new ArrayList<Attribute>());
		info.setElementClass(collections.get(0).getInfo().getElementClass());
		final List<CollectionElement> difference = new ArrayList<>();
		for (CollectionElement element : union(collections).getElements()) {
			if (!intersection.contains(element.getId())) {
				difference.add(element);
			}
		}
		return CollectionsEntry.create(info, difference);
	}


	private static CollectionsEntry difference(final List<CollectionsEntry> collections) {
		final HashSet<String> remove = new HashSet<String>();
		CollectionsEntry firstCollection = null;
		for (CollectionsEntry collection : collections) {
			if (firstCollection == null) firstCollection = collection;
			else {
				for (CollectionElement element : collection.getElements()) {
					remove.add(element.getId());
				}
			}
		}
		final CollectionInfo info = new CollectionInfo().attributes(new ArrayList<Attribute>());
		info.setElementClass(firstCollection.getInfo().getElementClass());
		final List<CollectionElement> difference = new ArrayList<>();
		for (CollectionElement element : firstCollection.getElements()) {
			if (!remove.contains(element.getId())) {
				difference.add(element);
			}
		}
		return CollectionsEntry.create(info, difference);
	}

}
