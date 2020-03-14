package transformer.classes;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;
import apimodels.CollectionInfo;
import apimodels.CompoundInfo;
import apimodels.CompoundInfoIdentifiers;
import apimodels.CompoundInfoStructure;
import apimodels.CompoundList;
import apimodels.Property;
import apimodels.TransformerQuery;
import transformer.Config;
import transformer.Config.CURIE;
import transformer.JSON;
import transformer.Transformer;
import transformer.Transformer.Query;
import transformer.Transformers;
import transformer.collection.Aggregator;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.collection.CollectionsEntry.CompoundCollection;
import transformer.exception.BadRequestException;
import transformer.exception.NotFoundException;
import transformer.exception.InternalServerError;

public class Compound extends TransformerClass {

	public static final String CLASS = "compound";
	public static final String BIOLINK_CLASS = "chemical substance";

	/**
	 * Logger
	 */
	final static Logger log = LoggerFactory.getLogger(Compound.class);


	@Override
	public Query getQuery(final TransformerQuery query) throws NotFoundException, BadRequestException {
		return new CompoundListQuery(query);
	}


	@Override
	public Query getQuery(final List<Property> controls, CollectionsEntry collection) throws BadRequestException {
		if (collection instanceof CompoundCollection) {
			return new CompoundListQuery(controls, ((CompoundCollection) collection).getCompounds());
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
		return new CompoundCollection(collectionInfo, compounds);
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
		compound.getNamesSynonyms().sort((names1, names2) -> {
			return Config.config.getCompoundNamePriority(names1.getSource()) - Config.config.getCompoundNamePriority(names2.getSource());
		});
		return compound;
	}


	private static String getBestIdentifier(final CompoundInfoIdentifiers identifiers, final CompoundInfoStructure structure) {
		if (identifiers.getChebi() != null) {
			return identifiers.getChebi();
		}
		if (identifiers.getChembl() != null) {
			return identifiers.getChembl();
		}
		if (identifiers.getDrugbank() != null) {
			return identifiers.getDrugbank();
		}
		if (identifiers.getPubchem() != null) {
			return identifiers.getPubchem();
		}
		if (identifiers.getMesh() != null) {
			return identifiers.getMesh();
		}
		if (identifiers.getHmdb() != null) {
			return identifiers.getHmdb();
		}
		if (structure.getInchi() != null) {
			return structure.getInchi();
		}
		if (structure.getInchikey() != null) {
			return structure.getInchikey();
		}
		if (identifiers.getUnii() != null) {
			return identifiers.getUnii();
		}
		if (identifiers.getKegg() != null) {
			return identifiers.getKegg();
		}
		if (identifiers.getGtopdb() != null) {
			return identifiers.getGtopdb();
		}
		if (identifiers.getChembank() != null) {
			return identifiers.getChembank();
		}
		if (identifiers.getDrugcentral() != null) {
			return identifiers.getDrugcentral();
		}
		return null;
	}


	static final class CompoundListQuery extends Query {

		private final CompoundInfo[] compounds;


		CompoundListQuery(final TransformerQuery query) throws NotFoundException, BadRequestException {
			super(query);
			this.compounds = getCollection(query.getCollectionId()).getCompounds();
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


	private static CompoundCollection getCollection(final String id) throws NotFoundException, BadRequestException {
		final CollectionsEntry collection = Collections.getCollection(id);
		if (collection instanceof CompoundCollection) {
			return (CompoundCollection) collection;
		}
		throw new BadRequestException("Collection " + collection.getId() + " is not a compound list");
	}


	public static CompoundList getCompoundList(final String id) throws NotFoundException, BadRequestException {
		final CompoundCollection collection = getCollection(id);
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


	public static CompoundList getCompoundByName(final String name) throws NotFoundException, BadRequestException {
		final List<CollectionsEntry> collections = new ArrayList<>();
		for (String producerName : Config.config.getCompoundSearchProducers()) {
			try {
				final CollectionsEntry response = getCompoundByName(producerName, name);
				collections.add(response);
			} catch (Exception e) {
				log.warn("Unable to obtain compound '" + name + "' from " + producerName, e);
			}
		}
		final CompoundCollection union = (CompoundCollection)Aggregator.union(collections);
		for (CompoundInfo compound: union.getCompounds()) {
			updateCompound(compound);
		}
		final String source = "Molecular Data Provider";
		union.getInfo().setSource(source);
		union.getInfo().addAttributesItem(new Attribute().name("query name").value(name).source(source));
		Collections.save(union);
		return getCompoundList(union.getId());
	}


	private static CollectionsEntry getCompoundByName(final String producerName, final String compoundName) throws Exception {
		final Transformer producer = Transformers.getTransformer(producerName);
		final String parameterName = producer.info.getParameters().get(0).getName();
		final List<Property> controls = new ArrayList<>();
		controls.add(new Property().name(parameterName).value(compoundName));
		final Query query = new Query(controls);
		final CollectionsEntry response = producer.transform(query, new CollectionInfo().elementClass(CLASS));
		return response;
	}


	public static CompoundInfo getCompoundById(final String compoundId) throws BadRequestException, NotFoundException {
		if (compoundId == null || compoundId.length() == 0) {
			throw new BadRequestException("Empty ID in the compound-by-id query");
		}
		return updateCompound(findCompoundById(Config.config.mapCuriePrefix(compoundId)));
	}


	public static CompoundInfo getCompoundByStructure(final String structure) throws BadRequestException, NotFoundException {
		if (structure == null || structure.length() == 0) {
			throw new BadRequestException("Empty string in the compound-by-structure query");
		}
		final CompoundInfo compound = (structure.startsWith("InChI=")) ? findCompoundByInChI(structure) : findCompoundBySmiles(structure);
		return updateCompound(compound);
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


	private static CompoundInfo findCompoundById(final String compoundId) throws NotFoundException {
		for (CURIE curie : Config.getConfig().getCuries().getAllCuries()) {
			if (curie.isPrefixOf(compoundId) && curie.getProducer() != null) {
				return findCompoundById(curie.getProducer(), compoundId);
			}
		}
		CompoundInfo compound = MyChem.Info.findCompoundById(compoundId);
		if (compound != null) {
			return compound;
		}
		throw new NotFoundException("Compound with id '" + compoundId + "' not found");
	}


	private static CompoundInfo findCompoundById(final String producer, final String compoundId) {
		try {
			final CollectionsEntry entry = getCompoundByName(producer, compoundId);
			if (entry.getInfo().getSize() == 0) {
				throw new NotFoundException(producer+": compound not found");
			}
			return ((CompoundCollection) entry).getCompounds()[0];
		} 
		catch (Exception e) {
			log.warn(e.getMessage(),e);
			throw new InternalServerError("Unable to obtain compound from "+producer+": " + e.getMessage());
		}
	}

}
