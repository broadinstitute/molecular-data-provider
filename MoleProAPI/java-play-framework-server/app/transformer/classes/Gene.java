package transformer.classes;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.core.type.TypeReference;

import apimodels.CollectionInfo;
import apimodels.GeneInfo;
import apimodels.GeneList;
import apimodels.Property;
import apimodels.TransformerInfo;
import apimodels.MoleProQuery;
import transformer.JSON;
import transformer.Transformer;
import transformer.Transformer.Query;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.collection.CollectionsEntry.GeneCollection;
import transformer.exception.BadRequestException;
import transformer.exception.NotFoundException;

public class Gene extends TransformerClass {

	public static final String CLASS = "gene";
	public static final String BIOLINK_CLASS = "Gene";


	@Override
	public Query getQuery(final MoleProQuery query) throws NotFoundException, BadRequestException {
		return new GeneListQuery(query);
	}


	@Override
	public Query getQuery(final List<Property> controls, CollectionsEntry collection) throws BadRequestException {
		if (collection instanceof GeneCollection) {
			return new GeneListQuery(controls, ((GeneCollection) collection).getGenes());
		}
		if (CLASS.equals(collection.getInfo().getElementClass())) {
			final GeneCollection geneCollection = new GeneCollection(collection.getInfo(), collection.getElements());
			return new GeneListQuery(controls, geneCollection.getGenes());
		}
		throw new BadRequestException("Collection " + collection.getId() + " is not a gene list");
	}


	@Override
	public CollectionsEntry getCollection(final CollectionInfo collectionInfo, final String response) throws Exception {
		//final GeneInfo[] genes = JSON.mapper.readValue(response, GeneInfo[].class);
		List<GeneInfo> src = JSON.mapper.readValue(response, new TypeReference<List<GeneInfo>>() { });
		List<GeneInfo> geneList = new ArrayList<>();
		for (GeneInfo gene : src) {
			if (gene.getSource() == null) {
				gene.setSource(collectionInfo.getSource());
			}
			MyGene.Info.addInfo(gene);
			if (gene.getGeneId() != null && gene.getIdentifiers() != null && gene.getIdentifiers().getEntrez() != null) {
				geneList.add(gene);
			}
		}
		collectionInfo.setElementClass(CLASS);
		return new GeneCollection(collectionInfo, geneList.toArray(new GeneInfo[geneList.size()]));
	}


	static final class GeneListQuery extends Query {

		private final GeneInfo[] genes;


		GeneListQuery(final MoleProQuery query) throws NotFoundException, BadRequestException {
			super(query);
			genes = getCollection(query.getCollectionId()).getGenes();
		}


		private GeneListQuery(List<Property> controls, GeneInfo[] genes) {
			super(controls);
			this.genes = genes;
		}


		public GeneInfo[] getGenes() {
			return genes;
		}


		@Override
		public Query query(final List<Property> controls) {
			return new GeneListQuery(controls, this.genes);
		}
	}


	private static GeneCollection getCollection(final String id) throws NotFoundException, BadRequestException {
		final CollectionsEntry collection = Collections.getCollection(id);
		if (collection instanceof GeneCollection) {
			return (GeneCollection) collection;
		}
		if (CLASS.equals(collection.getInfo().getElementClass())) {
			return new GeneCollection(collection.getInfo(), collection.getElements());
		}
		throw new BadRequestException("Collection " + collection.getId() + " is not a gene list");
	}


	public static GeneList getGeneList(final String id) throws NotFoundException, BadRequestException {
		final GeneCollection collection = getCollection(id);
		final GeneList geneList = new GeneList();
		geneList.setId(collection.getInfo().getId());
		geneList.setElementClass(collection.getInfo().getElementClass());
		geneList.setSize(collection.getInfo().getSize());
		geneList.setSource(collection.getInfo().getSource());
		geneList.setUrl(collection.getInfo().getUrl());
		geneList.setAttributes(collection.getInfo().getAttributes());
		for (GeneInfo gene : collection.getGenes()) {
			geneList.addElementsItem(gene);
		}
		return geneList;
	}


	public static class GeneListProducer extends Transformer {

		public GeneListProducer(TransformerInfo info) {
			super(info);
		}


		public CollectionsEntry transform(final Query query, final CollectionInfo collectionInfo) throws IOException, Exception {
			String propertyValue = query.getPropertyValue("genes");
			if (propertyValue == null) {
				throw new BadRequestException("required parameter 'genes' not specified");
			}
			final String[] geneIds = propertyValue.split(";");
			GeneInfo[] genes = new GeneInfo[geneIds.length];
			for (int i = 0; i < genes.length; i++) {
				final String geneId = geneIds[i].trim();
				if (geneId.contains(":")) {
					genes[i] = MyGene.Info.findGeneById(geneId, info.getName());
				} else {
					genes[i] = MyGene.Info.findGeneBySymbol(geneId, info.getName());
				}
			}
			collectionInfo.setElementClass(CLASS);
			return new GeneCollection(collectionInfo, genes);
		}
	}
}
