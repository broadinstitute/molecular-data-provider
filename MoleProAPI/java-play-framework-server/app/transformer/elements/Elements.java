package transformer.elements;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.Property;
import transformer.Config;
import transformer.MoleProDB;
import transformer.Transformer;
import transformer.Transformers;
import transformer.Config.CURIE;
import transformer.TransformerQuery;
import transformer.collection.Aggregator;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.exception.BadRequestException;
import transformer.exception.InternalServerError;
import transformer.exception.NotFoundException;

public class Elements {

	private static final String MOLEPRO_LOG = "molepro.log";

	private static final HashSet<String> CHEMICAL_CLASSES = new HashSet<>(Arrays.asList("SmallMolecule", "MolecularEntity", "ChemicalEntity", "ChemicalMixture", "MolecularMixture"));

	private static final String ANY_ELEMENT_CLASS = "any";
	private static final String COMPOUND_ELEMENT_CLASS = "compound";

	private static final Logger log = LoggerFactory.getLogger(Elements.class);


	public Elements() {

	}


	// elements by id

	public static Collection elementById(final String elementId, final String cache) throws BadRequestException {
		if (elementId == null || elementId.length() == 0) {
			throw new BadRequestException("Empty ID in the element-by-id query");
		}
		return elementsById(java.util.Collections.singletonList(elementId), cache).asCollection();
	}


	public static CollectionInfo elementById(final List<String> elementIds, final String cache) {
		return elementsById(elementIds, cache).getInfo();
	}


	private static CollectionsEntry elementsById(final List<String> elementIds, final String cache) {
		final CollectionsEntry collection = getElementsById(elementIds, cache);
		for (final String elementId : remainingIds(elementIds, collection.getElements())) {
			collection.getInfo().addAttributesItem(warningAttribute(elementId, "NotFoundException"));
		}
		Collections.save(collection, cache);
		return collection;
	}


	private static CollectionsEntry getElementsById(final List<String> elementIds, final String cache) {
		final CollectionInfo collectionInfo = newCollectionInfo(ANY_ELEMENT_CLASS);
		final List<CollectionElement> elements = new ArrayList<>();
		try {
			final Collection moleProDbCollection = MoleProDB.IdProducer.transform(elementIds).asCollection();
			for (Element element : moleProDbCollection.getElements()) {
				elements.add(new CollectionElement(element));
			}
			addAttributes(collectionInfo, moleProDbCollection);
		}
		catch (Exception e) {
			collectionInfo.addAttributesItem(warningAttribute(e, "InternalServerError"));
		}
		final CollectionsEntry collection = new CollectionsEntry(collectionInfo, elements.toArray(new CollectionElement[elements.size()]));
		return collection;
	}


	private static void addAttributes(final CollectionInfo collectionInfo, final Collection moleProDbCollection) {
		if (moleProDbCollection.getAttributes() != null)
			for (Attribute attribute : moleProDbCollection.getAttributes()) {
				if (attribute.getAttributeTypeId().startsWith(MOLEPRO_LOG)) {
					collectionInfo.addAttributesItem(attribute);
				}
			}
	}


	private static CollectionInfo newCollectionInfo(final String elementClass) {
		final CollectionInfo collectionInfo = new CollectionInfo();
		collectionInfo.setSource("MolePro");
		collectionInfo.setAttributes(new ArrayList<Attribute>());
		collectionInfo.setElementClass(elementClass);
		return collectionInfo;
	}


	private static HashSet<String> remainingIds(final List<String> elementIds, final CollectionElement[] collection) {
		final HashSet<String> remainingIds = new HashSet<>(elementIds);
		for (CollectionElement element : collection) {
			remainingIds.remove(element.getId());
			if (element.getElement().getAttributes() != null)
				for (Attribute attribute : element.getElement().getAttributes())
					if ("query name".equals(attribute.getOriginalAttributeName())) {
						remainingIds.remove(attribute.getValue());
					}
		}
		return remainingIds;
	}


	// compounds by name

	public static Element getCompoundById(final String compoundId, final String cache) throws BadRequestException, NotFoundException {
		if (compoundId == null || compoundId.length() == 0) {
			throw new BadRequestException("Empty ID in the compound-by-id query");
		}
		for (CollectionElement element : getElementsById(java.util.Collections.singletonList(compoundId), cache).getElements()) {
			if (CHEMICAL_CLASSES.contains(element.getElement().getBiolinkClass())) {
				return element.getElement();
			}
		}
		throw new NotFoundException("Compound '" + compoundId + "' not found");
	}


	public static CollectionInfo getCompoundsById(final List<String> compoundIds, final String cache) {
		final CollectionInfo collectionInfo = newCollectionInfo(COMPOUND_ELEMENT_CLASS);
		final List<CollectionElement> elements = new ArrayList<>();
		for (CollectionElement element : getElementsById(compoundIds, cache).getElements()) {
			if (CHEMICAL_CLASSES.contains(element.getElement().getBiolinkClass())) {
				elements.add(element);
			}
		}
		for (final String compoundId : remainingIds(compoundIds, elements.toArray(new CollectionElement[0]))) {
			try {
				elements.add(findCompoundById(compoundId));
			}
			catch (NotFoundException e) {
				collectionInfo.addAttributesItem(warningAttribute(e, "NotFoundException"));
			}
			catch (Exception e) {
				collectionInfo.addAttributesItem(warningAttribute(e, "InternalServerError"));
			}
			catch (InternalServerError e) {
				collectionInfo.addAttributesItem(warningAttribute(e, "InternalServerError"));
			}
		}
		final CollectionsEntry collection = new CollectionsEntry(collectionInfo, elements.toArray(new CollectionElement[elements.size()]));
		Collections.save(collection, cache);
		return collection.getInfo();
	}


	private static CollectionElement findCompoundById(final String srcCompoundId) throws NotFoundException {
		final String compoundId = Config.config.mapCuriePrefix(srcCompoundId);
		for (CURIE curie : Config.getConfig().getCuries().getAllCuries()) {
			if (curie.isPrefixOf(compoundId) && curie.getProducer() != null) {
				return findCompoundById(curie.getProducer(), compoundId);
			}
		}
		throw new NotFoundException("Compound with id '" + compoundId + "' not found");
	}


	private static CollectionElement findCompoundById(final String producer, final String compoundId) throws NotFoundException {
		try {
			final CollectionsEntry entry = getOneCompoundByName(producer, compoundId);
			if (entry.getInfo().getSize() == 0) {
				throw new NotFoundException(compoundId + " not found in " + producer);
			}
			return entry.getElements()[0];
		}
		catch (NotFoundException e) {
			log.warn(e.getMessage());
			throw new NotFoundException("Unable to obtain compound " + compoundId + " from " + producer + ": " + e.getMessage());
		}
		catch (Exception e) {
			log.warn(e.getMessage(), e);
			throw new InternalServerError("Unable to obtain compound " + compoundId + " from " + producer + ": " + e.getMessage());
		}
	}


	// elements by name

	public static Collection elementByName(final String name, final String cache) throws BadRequestException {
		if (name == null || name.length() == 0) {
			throw new BadRequestException("Empty ID in the element-by-name query");
		}
		return elementsByName(java.util.Collections.singletonList(name), cache).asCollection();
	}


	public static CollectionInfo elementByName(final List<String> names, final String cache) throws BadRequestException {
		return elementsByName(names, cache).getInfo();
	}


	public static CollectionsEntry elementsByName(final List<String> names, final String cache) throws BadRequestException {
		final CollectionsEntry collection = getElementsByName(names, cache);
		for (final String name : remainingIds(names, collection.getElements())) {
			collection.getInfo().addAttributesItem(warningAttribute(name, "NotFoundException"));
		}
		Collections.save(collection, cache);
		return collection;
	}


	public static CollectionsEntry getElementsByName(final List<String> names, final String cache) throws BadRequestException {
		final CollectionInfo collectionInfo = newCollectionInfo(ANY_ELEMENT_CLASS);
		final List<CollectionElement> elements = new ArrayList<>();
		try {
			final CollectionsEntry moleProDbCollection = MoleProDB.NameProducer.transform(names);
			final Collection union = Aggregator.union(java.util.Collections.singletonList(moleProDbCollection)).asCollection();
			for (Element element : union.getElements()) {
				elements.add(new CollectionElement(element));
			}
			addAttributes(collectionInfo, moleProDbCollection.asCollection());
		}
		catch (Exception e) {
			collectionInfo.addAttributesItem(warningAttribute(e, "InternalServerError"));
		}
		final CollectionsEntry collection = new CollectionsEntry(collectionInfo, elements.toArray(new CollectionElement[elements.size()]));
		return collection;
	}


	// compounds by name

	public static Collection getCompoundByName(final String name, String cache) throws NotFoundException, BadRequestException {
		String[] names = name.split(";");
		return compoundsByName(Arrays.asList(names), cache).asCollection();
	}


	public static CollectionInfo getCompoundsByName(final List<String> compoundNames, String cache) throws Exception {
		return compoundsByName(compoundNames, cache).getInfo();
	}


	private static CollectionsEntry compoundsByName(final List<String> names, String cache) throws BadRequestException {
		final CollectionsEntry elementCollection = getElementsByName(names, cache);
		final List<CollectionElement> elements = new ArrayList<>();
		for (CollectionElement element : elementCollection.getElements()) {
			if (CHEMICAL_CLASSES.contains(element.getElement().getBiolinkClass())) {
				elements.add(element);
			}
		}
		final CollectionInfo collectionInfo = newCollectionInfo(COMPOUND_ELEMENT_CLASS);
		addAttributes(collectionInfo, elementCollection.asCollection());
		final CollectionElement[] elementArray = elements.toArray(new CollectionElement[elements.size()]);
		for (final String name : remainingIds(names, elementArray)) {
			collectionInfo.addAttributesItem(warningAttribute(name, "NotFoundException"));
		}
		for (String name : names) {
			collectionInfo.addAttributesItem(new Attribute().originalAttributeName("query name").value(name).attributeSource("MolePro"));
		}
		final CollectionsEntry collection = new CollectionsEntry(collectionInfo, elementArray);
		Collections.save(collection, cache);
		return collection;
	}


	private static CollectionsEntry getOneCompoundByName(final String producerName, final String compoundName) throws Exception {
		final Transformer producer = Transformers.getTransformer(producerName);
		final String parameterName = producer.info.getParameters().get(0).getName();
		final List<Property> controls = new ArrayList<>();
		controls.add(new Property().name(parameterName).value(compoundName));
		final TransformerQuery query = new TransformerQuery(controls);
		final CollectionsEntry response = producer.transform(query, new CollectionInfo());
		return response;
	}


	public static Element getCompoundByStructure(final String structure, final String cache) throws BadRequestException, NotFoundException {
		if (structure == null || structure.length() == 0) {
			throw new BadRequestException("Empty string in the compound-by-structure query");
		}
		if (structure.startsWith("InChI=")) {
			return getCompoundById(structure, cache);
		}
		else
			throw new BadRequestException("Unsuported structure format");
	}


	// warning attributes

	private static Attribute warningAttribute(final Throwable e, final String name) {
		return warningAttribute(e.getMessage(), name);
	}


	private static Attribute warningAttribute(final String message, final String name) {
		return logAttribute("warning", message, name);
	}


	private static Attribute logAttribute(final String level, final String message, final String name) {
		return new Attribute().originalAttributeName(name).value(message).attributeTypeId(MOLEPRO_LOG + ":" + level).attributeSource("MolePro");
	}

}
