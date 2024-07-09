package transformer;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.Names;
import apimodels.Property;
import transformer.collection.CollectionsEntry;
import transformer.util.Cache;

public class MoleProDB {

	private final static Logger log = LoggerFactory.getLogger(MoleProDB.class);

	private final static String NODE_PRODUCER = "MoleProDB node producer";
	private final static String NAME_PRODUCER = "MoleProDB name producer";
	private final static String CONNECTIONS_TRANSFORMER = "MoleProDB connections transformer";

	private static final Element NO_ELEMENT_FOUND = new Element().id("NO_ELEMENT_FOUND");

	private static MoleProDBCache moleProDBCache = new MoleProDBCache(Config.config.getExpirationTimes().getMyChemInfo());


	public static boolean addInfo(final Element element) {
		if (element == null || element.getIdentifiers() == null || element.getId() == null) {
			return true;
		}
		if (isMoleProDbElement(element) || hasMoleProName(element)) {
			return true;
		}
		Element cachedElement = findCachedElement(element);
		if (cachedElement == NO_ELEMENT_FOUND) {
			return true;
		}
		if (cachedElement == null)
			try {
				cachedElement = download(element);
				cachedElement = save(cachedElement);
			}
			catch (Exception e) {
				log.warn("Failed to obtain MoleProDB info for " + element.getId(), e);
			}
		return addInfo(element, cachedElement);
	}


	private static boolean addInfo(final Element element, final Element cachedElement) {
		if (cachedElement == null) {
			return false;
		}
		for (Entry<String,Object> identifier : cachedElement.getIdentifiers().entrySet()) {
			if (!element.getIdentifiers().containsKey(identifier.getKey())) {
				element.getIdentifiers().put(identifier.getKey(), identifier.getValue());
			}
		}
		if (cachedElement.getNamesSynonyms() == null) {
			log.info("No MoleProDB names for " + cachedElement.getId());
		}
		else {
			final Set<String> nameSources = new HashSet<>();
			if (element.getNamesSynonyms() != null)
				element.getNamesSynonyms().stream().map(Names::getSource).collect(Collectors.toSet());
			for (Names names : cachedElement.getNamesSynonyms()) {
				if (!nameSources.contains(names.getSource())) {
					element.addNamesSynonymsItem(names);
				}
			}
		}
		return true;
	}


	private static Element download(final Element srcElement) throws Exception {
		Element element = download(Collections.singletonList(srcElement.getId()));
		if (element != null) {
			return element;
		}
		final ArrayList<String> ids = new ArrayList<String>();
		for (String field : Config.config.getIdentifierPriority(srcElement.getBiolinkClass())) {
			if (srcElement.getIdentifiers().containsKey(field)) {
				for (String id : identifierValues(srcElement.getIdentifiers().get(field))) {
					ids.add(id);
				}
			}
		}
		element = download(ids);
		if (element == null) {
			moleProDBCache.noElementFound(srcElement);
		}
		return element;
	}


	private static Element download(final List<String> ids) {
		try {
			final Collection collection = MoleProDB.IdProducer.transform(ids).asCollection();
			if (collection != null && collection.getSize() > 0) {
				if (collection.getSize() > 1) {
					log.info("Obtained multiple MoleProDB elements for " + ids);
				}
				return collection.getElements().get(0);
			}
		}
		catch (Exception e) {
			log.warn("Failed to obtain element from MoleProDB for " + ids + ": " + e, e);
		}
		log.info("No element found for " + ids);
		return null;
	}


	private static Element save(final Element srcElement) {
		if (srcElement == null) {
			return null;
		}
		final Element cachedElement = new Element();
		cachedElement.setId(srcElement.getId());
		cachedElement.setIdentifiers(srcElement.getIdentifiers());
		for (Names names : srcElement.getNamesSynonyms()) {
			if ("MolePro".equals(names.getSource())) {
				cachedElement.addNamesSynonymsItem(names);
			}
		}
		for (String idField : cachedElement.getIdentifiers().keySet()) {
			moleProDBCache.addKeySet(idField);
		}
		moleProDBCache.save(cachedElement);
		return cachedElement;
	}


	private static boolean isMoleProDbElement(final Element element) {
		return NODE_PRODUCER.equals(element.getProvidedBy()) || CONNECTIONS_TRANSFORMER.equals(element.getProvidedBy());
	}


	private static boolean hasMoleProName(final Element element) {
		if (element.getNamesSynonyms() == null) {
			return false;
		}
		for (Names names : element.getNamesSynonyms()) {
			if ("MolePro".equals(names.getSource())) {
				return true;
			}
		}
		return false;
	}


	private static Element findCachedElement(final Element srcElement) {
		Element cachedElement = null;
		String idField = findIdField(srcElement);
		if (idField != null) {
			moleProDBCache.addKeySet(idField);
			cachedElement = moleProDBCache.get(idField, srcElement.getId());
		}
		if (cachedElement != null) {
			return cachedElement;
		}
		if (cachedElement == null) {
			for (String field : Config.config.getIdentifierPriority(srcElement.getBiolinkClass())) {
				if (srcElement.getIdentifiers().containsKey(field)) {
					for (String id : identifierValues(srcElement.getIdentifiers().get(field))) {
						cachedElement = moleProDBCache.get(field, id);
						if (cachedElement != null) {
							return cachedElement;
						}
					}
				}
			}
		}
		return cachedElement;
	}


	private static String findIdField(final Element element) {
		if (element.getId() == null) {
			return null;
		}
		for (Entry<String,Object> identifier : element.getIdentifiers().entrySet()) {
			if (element.getId().equals(identifier.getValue())) {
				return identifier.getKey();
			}
		}
		return null;
	}


	@SuppressWarnings("unchecked")
	private static String[] identifierValues(final Object values) {
		if (values instanceof String) {
			return new String[] { (String)values };
		}
		if (values instanceof String[]) {
			return (String[])values;
		}
		if (values instanceof ArrayList) {
			return ((ArrayList<Object>)values).stream().map(Object::toString).toArray(String[]::new);
		}
		return new String[0];
	}

	public final static Producer IdProducer = new Producer(NODE_PRODUCER, "id");

	public final static Producer NameProducer = new Producer(NAME_PRODUCER, "name");


	public static class Producer {

		private final String transformerName;
		private final String propertyName;


		public Producer(String transformerName, String propertyName) {
			super();
			this.transformerName = transformerName;
			this.propertyName = propertyName;
		}


		public CollectionsEntry transform(final List<String> ids) throws Exception {
			final Transformer MoleProDbProducer = Transformers.getTransformer(transformerName);
			final List<Property> controls = new ArrayList<>();
			for (String id : ids) {
				controls.add(new Property().name(propertyName).value(id));
			}
			final TransformerQuery query = new TransformerQuery(controls);
			return MoleProDbProducer.transform(query, new CollectionInfo());
		}
	}


	static class MoleProDBCache extends Cache<String,String,Element> {

		public MoleProDBCache(final long expirationTime) {
			super(expirationTime);
			for (String field : Config.config.getIdentifierPriority("")) {
				addKeySet(field);
			}
		}


		@SuppressWarnings("unchecked")
		@Override
		protected List<KeyPair<String,String>> getKeys(final Element element) {
			List<KeyPair<String,String>> keys = new ArrayList<KeyPair<String,String>>();
			for (Entry<String,Object> identifier : element.getIdentifiers().entrySet()) {
				if (identifier.getValue() instanceof String) {
					keys.add(new KeyPair<String,String>(identifier.getKey(), (String)identifier.getValue()));
				}
				if (identifier.getValue() instanceof String[]) {
					for (String value : (String[])identifier.getValue())
						keys.add(new KeyPair<String,String>(identifier.getKey(), value));
				}
				if (identifier.getValue() instanceof ArrayList) {
					for (Object value : (ArrayList<Object>)identifier.getValue()) {
						keys.add(new KeyPair<String,String>(identifier.getKey(), value.toString()));
					}
				}
			}
			return keys;
		}


		void noElementFound(final Element srcElement) {
			for (KeyPair<String,String> keyPair : getKeys(srcElement)) {
				if (keyPair.keySet != null && keyPair.key != null) {
					addKeySet(keyPair.keySet);
					put(keyPair.keySet, keyPair.key, NO_ELEMENT_FOUND);
				}

			}
		}

	}


	public static int size() {
		return moleProDBCache.size();
	}
}
