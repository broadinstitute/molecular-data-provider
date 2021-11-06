package transformer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;
import apimodels.CollectionInfo;
import apimodels.KmAttribute;
import apimodels.KnowledgeMap;
import apimodels.Predicate;
import apimodels.TransformerInfo;
import apimodels.TransformerInfoProperties;
import apimodels.MoleProQuery;
import apimodels.Node;
import apimodels.Property;
import transformer.classes.Compound;
import transformer.classes.Gene;
import transformer.classes.None;
import transformer.classes.TransformerClass;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.exception.BadRequestException;
import transformer.exception.InternalServerError;
import transformer.exception.NotFoundException;

public abstract class Transformer {

	final static Logger log = LoggerFactory.getLogger(Config.class);
	
	private final static TransformerInfo.FunctionEnum PRODUCER = TransformerInfo.FunctionEnum.PRODUCER;

	public final TransformerInfo info;

	protected final TransformerClass inputClass;

	protected final TransformerClass outputClass;


	protected Transformer(final TransformerInfo info) {
		super();
		this.info = info;
		if (this.info.getKnowledgeMap() == null) {
			this.info.setKnowledgeMap(buildKnowledgeMap(info));
		}
		this.inputClass = getInputClass(info.getKnowledgeMap(), info.getName());
		this.outputClass = getOutputClass(info.getKnowledgeMap(), info.getName());
		TransformerInfoProperties properties = this.info.getProperties();
		if (properties == null) {
			properties = new TransformerInfoProperties();
			this.info.setProperties(properties);
		}
		if (properties.getSourceUrl() == null) {
			properties.setSourceUrl("");
		}
		if (properties.getSourceVersion() == null) {
			properties.setSourceVersion("");
		}
		if (properties.getTermsOfService() == null) {
			properties.setTermsOfService("");
		}
		// migrate transformer info to version 2.3
		final KnowledgeMap knowledgeMap = this.info.getKnowledgeMap();
		if (knowledgeMap.getEdges() == null) {
			knowledgeMap.setEdges(knowledgeMap.getPredicates());
			knowledgeMap.setPredicates(null);
		}
		if (knowledgeMap.getNodes() != null) {
			for (Node node : knowledgeMap.getNodes().values()) {
				if (node.getAttributes() != null)
					for (KmAttribute attr : node.getAttributes()) {
						if (attr.getAttributeTypeId() == null) {
							attr.setAttributeTypeId(attr.getType());
							attr.setType(null);
						}
					}
			}
		}
		if (knowledgeMap.getEdges() != null) {
			for (Predicate predicate : knowledgeMap.getEdges()) {
				if (predicate.getAttributes() != null)
					for (KmAttribute attr : predicate.getAttributes()) {
						if (attr.getAttributeTypeId() == null) {
							attr.setAttributeTypeId(attr.getType());
							attr.setType(null);
						}
					}
			}
		}
	}


	public CollectionInfo transform(final MoleProQuery moleproQuery, String cache) throws Exception {
		try {
			final Query query = mkQuery(moleproQuery, cache);
			final CollectionInfo collectionInfo = createCollection(moleproQuery);
			final CollectionsEntry collection = transform(query, collectionInfo);
			Collections.save(collection);
			return collection.getInfo();
		} catch (IOException e) {
			throw new InternalServerError(info.getName() + " failed: " + e.getMessage(), e);
		}
	}


	private Query mkQuery(final MoleProQuery moleproQuery, String cache) throws NotFoundException, BadRequestException {
		if (info.getVersion().startsWith("1.") || info.getVersion().startsWith("2.0."))
			return inputClass.getQuery(moleproQuery, cache);
		boolean hasInput = !(PRODUCER.equals(info.getFunction()) || "none".equals(info.getKnowledgeMap().getInputClass()));
		return new TransformerQuery(moleproQuery, cache, hasInput);
	}


	public abstract CollectionsEntry transform(Query query, CollectionInfo collectionInfo) throws Exception;


	protected CollectionInfo createCollection(final MoleProQuery query) {
		final CollectionInfo collectionInfo = new CollectionInfo();
		collectionInfo.setSource(info.getName());
		collectionInfo.setAttributes(new ArrayList<Attribute>());
		for (Property property : query.getControls()) {
			final Attribute attribute = new Attribute().originalAttributeName(property.getName()).attributeSource(info.getName()).value(property.getValue());
			collectionInfo.addAttributesItem(attribute);
		}
		return collectionInfo;
	}


	private static TransformerClass getInputClass(final KnowledgeMap kmap, final String name) {
		if (Compound.CLASS.equals(kmap.getInputClass())) {
			return new transformer.classes.Compound();
		}
		if (Gene.CLASS.equals(kmap.getInputClass())) {
			return new transformer.classes.Gene();
		}
		if (kmap.getInputClass() == null || None.CLASS.equals(kmap.getInputClass())) {
			return new transformer.classes.None();
		}
		return new transformer.classes.Other(kmap.getOutputClass());
	}


	private static TransformerClass getOutputClass(final KnowledgeMap kmap, final String name) {
		if (Compound.CLASS.equals(kmap.getOutputClass())) {
			return new transformer.classes.Compound();
		}
		if (Gene.CLASS.equals(kmap.getOutputClass())) {
			return new transformer.classes.Gene();
		}
		if (kmap.getOutputClass() == null || None.CLASS.equals(kmap.getOutputClass())) {
			throw new InternalServerError("Output class '" + kmap.getInputClass() + "' for '" + name + "' is not supported");
		}
		return new transformer.classes.Other(kmap.getOutputClass());
	}


	private static KnowledgeMap buildKnowledgeMap(final TransformerInfo info) {
		final KnowledgeMap kmap = new KnowledgeMap();
		kmap.setInputClass(getInputClass(info));
		kmap.setOutputClass(Gene.CLASS);
		kmap.setEdges(new ArrayList<Predicate>());
		final String subject = kmap.getInputClass().toString();
		if (!None.CLASS.equals(subject)) {
			String predicate = "related to";
			final String object = kmap.getOutputClass().toString();
			kmap.addEdgesItem(new Predicate().subject(subject).predicate(predicate)._object(object));
		}
		return kmap;
	}


	private static String getInputClass(final TransformerInfo info) {
		if (info.getFunction() == TransformerInfo.FunctionEnum.PRODUCER) {
			return None.CLASS;
		}
		if (info.getFunction() == TransformerInfo.FunctionEnum.AGGREGATOR) {
			return None.CLASS;
		}
		return Gene.CLASS;
	}


	public static class Query {
		private final List<Property> controls;


		public Query(final MoleProQuery query) {
			controls = query.getControls();
		}


		public Query(final List<Property> controls) {
			super();
			this.controls = controls;
		}


		public List<Property> getControls() {
			return controls;
		}


		public String getPropertyValue(String name) {
			for (Property property : controls) {
				if (name.equals(property.getName())) {
					return property.getValue();
				}
			}
			return null;
		}


		public Query query(final List<Property> controls) {
			return new Query(controls);
		}
	}
}
