package transformer.classes;

import java.util.List;

import apimodels.CollectionInfo;
import apimodels.Property;
import apimodels.TransformerQuery;
import transformer.Transformer;
import transformer.collection.CollectionsEntry;
import transformer.exception.BadRequestException;
import transformer.exception.NotFoundException;

public abstract class TransformerClass {

	public abstract Transformer.Query getQuery(TransformerQuery query) throws NotFoundException, BadRequestException;


	public abstract Transformer.Query getQuery(final List<Property> controls, CollectionsEntry entry) throws BadRequestException;


	public abstract CollectionsEntry getCollection(CollectionInfo collectionInfo, String response) throws Exception;
}
