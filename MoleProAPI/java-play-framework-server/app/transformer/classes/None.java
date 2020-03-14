package transformer.classes;

import java.util.List;

import apimodels.CollectionInfo;
import apimodels.Property;
import apimodels.TransformerQuery;
import transformer.Transformer.Query;
import transformer.collection.CollectionsEntry;
import transformer.exception.InternalServerError;

public class None extends TransformerClass {

	public static final String CLASS = "none";


	@Override
	public Query getQuery(TransformerQuery query) {
		return new Query(query);
	}


	@Override
	public Query getQuery(final List<Property> controls, CollectionsEntry entry) {
		return new Query(controls);
	}


	@Override
	public CollectionsEntry getCollection(CollectionInfo collectionInfo, String response) {
		throw new InternalServerError("Output class should not be NONE");
	}

}
