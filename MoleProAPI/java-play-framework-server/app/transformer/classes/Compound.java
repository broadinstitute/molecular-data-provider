package transformer.classes;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.CompoundInfo;
import apimodels.CompoundInfoIdentifiers;
import apimodels.CompoundInfoStructure;
import apimodels.CompoundList;
import apimodels.Element;
import apimodels.Names;
import apimodels.Property;
import apimodels.MoleProQuery;
import transformer.Config;
import transformer.MoleProDB;
import transformer.Config.CURIE;
import transformer.Transformer;
import transformer.Transformer.Query;
import transformer.Transformers;
import transformer.collection.Aggregator;
import transformer.collection.CollectionElement;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.collection.CollectionsEntry.CompoundCollection;
import transformer.exception.BadRequestException;
import transformer.exception.NotFoundException;
import transformer.util.JSON;
import transformer.exception.InternalServerError;

public class Compound extends TransformerClass {

	public static final String CLASS = "compound";
	public static final String BIOLINK_CLASS = "SmallMolecule";

	/**
	 * Logger
	 */
	final static Logger log = LoggerFactory.getLogger(Compound.class);


	@Override
	public Query getQuery(final MoleProQuery query, String cache) throws NotFoundException, BadRequestException {
		return new CompoundListQuery(query, cache);
	}


	@Override
	public Query getQuery(final List<Property> controls, CollectionsEntry collection) throws BadRequestException {
		if (collection instanceof CompoundCollection) {
			return new CompoundListQuery(controls, ((CompoundCollection)collection).getCompounds());
		}
		if (CLASS.equals(collection.getInfo().getElementClass())) {
			CompoundCollection compoundCollection = new CompoundCollection(collection.getInfo(), collection.getElements());
			return new CompoundListQuery(controls, compoundCollection.getCompounds());
		}

		throw new BadRequestException("Collection " + collection.getId() + " is not a compound list");
	}


	@Override
	public CollectionsEntry getCollection(final CollectionInfo collectionInfo, final String response) throws Exception {
		final CompoundInfo[] compounds = JSON.mapper.readValue(response, CompoundInfo[].class);
		for (CompoundInfo compound : compounds) {
			if (compound.getSource() == null) {
				compound.setSource(collectionInfo.getSource());
			}
			updateCompound(compound);
		}
		collectionInfo.setElementClass(CLASS);
		return new CompoundCollection(collectionInfo, filter(compounds));
	}


	private final CompoundInfo[] filter(final CompoundInfo[] src) {
		final List<CompoundInfo> compounds = new ArrayList<>();
		for (CompoundInfo compound : src) {
			if (compound.getCompoundId() != null) {
				compounds.add(compound);
			}
		}
		return compounds.toArray(new CompoundInfo[compounds.size()]);
	}


	public static void updateCompound(final Element compound) {
		MyChem.Info.addInfo(compound);
		PubChem.addInfo(compound);
		// update primary identifier
		final String compoundId = getBestIdentifier(compound.getIdentifiers());
		if (compoundId != null) {
			compound.setId(compoundId);
		}
		// update name order
		if (compound.getNamesSynonyms() == null) {
			compound.setNamesSynonyms(new ArrayList<Names>());
		}
		compound.getNamesSynonyms().sort((names1, names2) -> {
			return Config.config.getCompoundNamePriority(names1.getSource()) - Config.config.getCompoundNamePriority(names2.getSource());
		});
	}


	private static String getBestIdentifier(Map<String,Object> identifiers) {
		final String[] idKeys = { "chebi", "chembl", "drugbank", "pubchem", "unii", "inchikey" };
		for (String key : idKeys) {
			if (identifiers.containsKey(key)) {
				if (identifiers.get(key) instanceof String) {
					return (String)identifiers.get(key);
				}
				if (identifiers.get(key) instanceof String[]) {
					return ((String[])identifiers.get(key))[0];
				}
			}
		}
		return null;
	}


	private static CompoundInfo updateCompound(final CompoundInfo compound) {
		MyChem.Info.addInfo(compound);
		PubChem.addInfo(compound);
		// update primary identifier
		final String compoundId = getBestIdentifier(compound.getIdentifiers(), compound.getStructure());
		if (compoundId != null) {
			compound.setCompoundId(compoundId);
		}
		// update name order
		if (compound.getNamesSynonyms() == null) {
			compound.setNamesSynonyms(new ArrayList<Names>());
		}
		compound.getNamesSynonyms().sort((names1, names2) -> {
			return Config.config.getCompoundNamePriority(names1.getSource()) - Config.config.getCompoundNamePriority(names2.getSource());
		});
		return compound;
	}


	private static String getBestIdentifier(final CompoundInfoIdentifiers identifiers, final CompoundInfoStructure structure) {
		if (identifiers != null && identifiers.getChebi() != null) {
			return identifiers.getChebi();
		}
		if (identifiers != null && identifiers.getChembl() != null) {
			return identifiers.getChembl();
		}
		if (identifiers != null && identifiers.getDrugbank() != null) {
			return identifiers.getDrugbank();
		}
		if (identifiers != null && identifiers.getPubchem() != null) {
			return identifiers.getPubchem();
		}
		if (identifiers != null && identifiers.getMesh() != null) {
			return identifiers.getMesh();
		}
		if (identifiers != null && identifiers.getHmdb() != null) {
			return identifiers.getHmdb();
		}
		if (structure != null && structure.getInchi() != null) {
			return structure.getInchi();
		}
		if (structure != null && structure.getInchikey() != null) {
			return structure.getInchikey();
		}
		if (identifiers != null && identifiers.getUnii() != null) {
			return identifiers.getUnii();
		}
		if (identifiers != null && identifiers.getKegg() != null) {
			return identifiers.getKegg();
		}
		if (identifiers != null && identifiers.getGtopdb() != null) {
			return identifiers.getGtopdb();
		}
		if (identifiers != null && identifiers.getChembank() != null) {
			return identifiers.getChembank();
		}
		if (identifiers != null && identifiers.getDrugcentral() != null) {
			return identifiers.getDrugcentral();
		}
		return null;
	}


	static final class CompoundListQuery extends Query {

		private final CompoundInfo[] compounds;


		CompoundListQuery(final MoleProQuery query, String cache) throws NotFoundException, BadRequestException {
			super(query);
			this.compounds = getCollection(query.getCollectionId(), cache).getCompounds();
		}


		private CompoundListQuery(final List<Property> controls, final CompoundInfo[] compounds) {
			super(controls);
			this.compounds = compounds;
		}


		public CompoundInfo[] getCompounds() {
			return compounds;
		}


		@Override
		public Query query(final List<Property> controls) {
			return new CompoundListQuery(controls, this.compounds);
		}
	}


	private static CompoundCollection getCollection(final String id, String cache) throws NotFoundException, BadRequestException {
		final CollectionsEntry collection = Collections.getCollection(id, cache);
		if (collection instanceof CompoundCollection) {
			return (CompoundCollection)collection;
		}
		if (CLASS.equals(collection.getInfo().getElementClass())) {
			return new CompoundCollection(collection.getInfo(), collection.getElements());
		}
		throw new BadRequestException("Collection " + collection.getId() + " is not a compound list");
	}


	public static CompoundList getCompoundList(final String id, String cache) throws NotFoundException, BadRequestException {
		final CompoundCollection collection = getCollection(id, cache);
		final CompoundList compoundList = new CompoundList();
		compoundList.setId(collection.getInfo().getId());
		compoundList.setElementClass(collection.getInfo().getElementClass());
		compoundList.setSize(collection.getInfo().getSize());
		compoundList.setSource(collection.getInfo().getSource());
		compoundList.setUrl(collection.getInfo().getUrl());
		compoundList.setAttributes(collection.getInfo().getAttributes());
		for (CompoundInfo compound : collection.getCompounds()) {
			compoundList.addElementsItem(compound);
		}
		return compoundList;
	}


	public static Collection getCompoundByName(final String name, String cache) throws NotFoundException, BadRequestException {
		String[] names = name.split(";");
		return compoundsByName(Arrays.asList(names), cache).asCollection();
	}


	public static CollectionInfo getCompoundsByName(final List<String> compoundNames, String cache) throws Exception {
		return compoundsByName(compoundNames, cache).getInfo();
	}


	private static CollectionsEntry compoundsByName(final List<String> names, String cache) throws NotFoundException, BadRequestException {
		final CollectionInfo collectionInfo = new CollectionInfo();
		final List<CollectionsEntry> collections = new ArrayList<>();
		final HashSet<String> remainingNames = new HashSet<>(names);
		try {
			final CollectionsEntry moleProDbCollection = MoleProDB.NameProducer.transform(names);
			moleProDbCollection.getInfo().setElementClass(CLASS);
			collections.add(moleProDbCollection);
			for (Element element : moleProDbCollection.asCollection().getElements()) {
				if (element.getAttributes() != null)
					for (Attribute attribute : element.getAttributes())
						if ("query name".equals(attribute.getOriginalAttributeName())) {
							remainingNames.remove(attribute.getValue());
						}
			}
		}
		catch (Exception e) {
			collectionInfo.addAttributesItem(warningAttribute(e, "InternalServerError"));
		}
		if (remainingNames.size() > 0) {
			collections.add(compoundsByName(remainingNames));
		}
		final CollectionsEntry union = Aggregator.union(collections);
		final String source = "MolePro";
		union.getInfo().setSource(source);
		for (String name : names) {
			union.getInfo().addAttributesItem(new Attribute().originalAttributeName("query name").value(name).attributeSource(source));
		}
		if (collectionInfo.getAttributes() != null)
			for (Attribute attribute : collectionInfo.getAttributes()) {
				union.getInfo().addAttributesItem(attribute);
			}
		Collections.save(union, cache);
		return union;
	}


	private static CompoundCollection compoundsByName(final HashSet<String> remainingNames) {
		final List<CollectionsEntry> collections = new ArrayList<>();
		for (String name : remainingNames) {
			for (String producerName : Config.config.getCompoundSearchProducers()) {
				try {
					final CollectionsEntry response = getOneCompoundByName(producerName, name);
					collections.add(response);
				}
				catch (Exception e) {
					log.warn("Unable to obtain compound '" + name + "' from " + producerName, e);
				}
			}
		}
		final CompoundCollection union = (CompoundCollection)Aggregator.union(collections);
		for (CompoundInfo compound : union.getCompounds()) {
			updateCompound(compound);
		}
		return union;
	}


	private static CollectionsEntry getOneCompoundByName(final String producerName, final String compoundName) throws Exception {
		final Transformer producer = Transformers.getTransformer(producerName);
		final String parameterName = producer.info.getParameters().get(0).getName();
		final List<Property> controls = new ArrayList<>();
		controls.add(new Property().name(parameterName).value(compoundName));
		final Query query = new Query(controls);
		final CollectionsEntry response = producer.transform(query, new CollectionInfo().elementClass(CLASS));
		return response;
	}


	public static Element getCompoundById(final String compoundId) throws BadRequestException, NotFoundException {
		if (compoundId == null || compoundId.length() == 0) {
			throw new BadRequestException("Empty ID in the compound-by-id query");
		}
		try {
			final Collection moleProDbCollection = MoleProDB.IdProducer.transform(java.util.Collections.singletonList(compoundId)).asCollection();
			if (moleProDbCollection.getSize() > 1) {
				log.warn("Obtained multiple compounds from MoleProDB for " + compoundId);
			}
			if (moleProDbCollection.getSize() > 0) {
				return moleProDbCollection.getElements().get(0);
			}
		}
		catch (Exception e) {
			log.warn("Failed to obtain compound from MoleProDB", e);
		}
		final CompoundInfo compound = updateCompound(findCompoundById(compoundId).getCompoundInfo());
		return new CollectionElement.CompoundElement(compound).getElement();
	}


	public static CollectionInfo getCompoundsById(final List<String> compoundIds, String cache) {
		final CollectionInfo collectionInfo = new CollectionInfo();
		collectionInfo.setSource("MolePro");
		collectionInfo.setAttributes(new ArrayList<Attribute>());
		collectionInfo.setElementClass(CLASS);
		final List<CollectionElement> elements = new ArrayList<>();
		final HashSet<String> remainingIds = new HashSet<>(compoundIds);
		try {
			final Collection moleProDbCollection = MoleProDB.IdProducer.transform(compoundIds).asCollection();
			for (Element element : moleProDbCollection.getElements()) {
				elements.add(new CollectionElement.ElementElement(element));
				remainingIds.remove(element.getId());
				if (element.getAttributes() != null)
					for (Attribute attribute : element.getAttributes())
						if ("query name".equals(attribute.getOriginalAttributeName())) {
							remainingIds.remove(attribute.getValue());
						}
			}
		}
		catch (Exception e) {
			collectionInfo.addAttributesItem(warningAttribute(e, "InternalServerError"));
		}
		for (final String compoundId : remainingIds) {
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


	private static Attribute warningAttribute(Throwable e, String name) {
		return new Attribute().originalAttributeName(name).value(e.getMessage()).attributeTypeId("molepro:warning").attributeSource("MolePro");
	}


	public static Element getCompoundByStructure(final String structure) throws BadRequestException, NotFoundException {
		if (structure == null || structure.length() == 0) {
			throw new BadRequestException("Empty string in the compound-by-structure query");
		}
		final CompoundInfo compound = (structure.startsWith("InChI=")) ? findCompoundByInChI(structure) : findCompoundBySmiles(structure);
		return new CollectionElement.CompoundElement(updateCompound(compound)).getElement();
	}


	private static CompoundInfo findCompoundByInChI(final String structure) throws NotFoundException {
		CompoundInfo compound = PubChem.findCompoundByInChI(structure);
		if (compound != null) {
			return compound;
		}
		throw new NotFoundException("Compound not found");
	}


	private static CompoundInfo findCompoundBySmiles(final String structure) throws NotFoundException {
		CompoundInfo compound = PubChem.findCompoundBySmiles(structure);
		if (compound != null) {
			return compound;
		}
		throw new NotFoundException("Compound not found");
	}


	private static CollectionElement findCompoundById(final String srcCompoundId) throws NotFoundException {
		final String compoundId = Config.config.mapCuriePrefix(srcCompoundId);
		for (CURIE curie : Config.getConfig().getCuries().getAllCuries()) {
			if (curie.isPrefixOf(compoundId) && curie.getProducer() != null) {
				return findCompoundById(curie.getProducer(), compoundId);
			}
		}
		CompoundInfo compound = MyChem.Info.findCompoundById(compoundId);
		if (compound != null) {
			return new CollectionElement.CompoundElement(compound);
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

}
