package transformer;

import java.io.IOException;
import java.util.ArrayList;

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
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.exception.BadRequestException;
import transformer.exception.InternalServerError;
import transformer.exception.NotFoundException;

public abstract class Transformer {

	final static Logger log = LoggerFactory.getLogger(Config.class);

	private final static TransformerInfo.FunctionEnum PRODUCER = TransformerInfo.FunctionEnum.PRODUCER;

	public final TransformerInfo info;


	protected Transformer(final TransformerInfo info) {
		super();
		this.info = info;
		if (this.info.getKnowledgeMap() == null) {
			log.error("No knowledge map info for " + info.getName());
		}
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
			final TransformerQuery query = mkQuery(moleproQuery, cache);
			final CollectionInfo collectionInfo = createCollection(moleproQuery);
			final CollectionsEntry collection = transform(query, collectionInfo);
			Collections.save(collection);
			return collection.getInfo();
		}
		catch (IOException e) {
			throw new InternalServerError(info.getName() + " failed: " + e.getMessage(), e);
		}
	}


	private TransformerQuery mkQuery(final MoleProQuery moleproQuery, String cache) throws NotFoundException, BadRequestException {
		boolean hasInput = !(PRODUCER.equals(info.getFunction()) || "none".equals(info.getKnowledgeMap().getInputClass()));
		return new TransformerQuery(moleproQuery, cache, hasInput);
	}


	public abstract CollectionsEntry transform(TransformerQuery query, CollectionInfo collectionInfo) throws Exception;


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

}
