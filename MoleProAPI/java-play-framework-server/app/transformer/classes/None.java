package transformer.classes;

import java.util.List;

import apimodels.CollectionInfo;
import apimodels.Property;
import apimodels.MoleProQuery;
import transformer.Transformer.Query;
import transformer.collection.CollectionsEntry;
import transformer.exception.InternalServerError;

public class None extends TransformerClass {

	public static final String CLASS = "none";


	@Override
	public Query getQuery(final MoleProQuery query, String cache) {
		return new Query(query);
	}


	@Override
	public Query getQuery(final List<Property> controls, final CollectionsEntry entry) {
		return new Query(controls);
	}


	@Override
	public CollectionsEntry getCollection(final CollectionInfo collectionInfo, final String response) {
		throw new InternalServerError("Output class should not be NONE");
	}

}
