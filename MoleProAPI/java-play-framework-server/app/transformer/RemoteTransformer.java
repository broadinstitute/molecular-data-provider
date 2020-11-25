package transformer;

import java.net.URL;

import apimodels.CollectionInfo;
import apimodels.TransformerInfo;
import transformer.collection.CollectionsEntry;
import transformer.util.HTTP;
import transformer.util.JSON;
import transformer.Transformer.Query;
import transformer.classes.Other;

public class RemoteTransformer extends Transformer {

	static Transformer createFrom(final TransformerInfo info) {
		return new RemoteTransformer(info);
	}


	protected RemoteTransformer(final TransformerInfo info) {
		super(info);
	}


	@Override
	public CollectionsEntry transform(final Query query, final CollectionInfo collectionInfo) throws Exception {
		final URL url = new URL(info.getUrl() + "/transform");
		log.debug(info.getName() + " @ " + url);
		final String json = JSON.mapper.writeValueAsString(query);
		final String response = HTTP.post(url, json);
		final CollectionsEntry collection = getCollection(collectionInfo, response);
		return collection;
	}


	private CollectionsEntry getCollection(final CollectionInfo collectionInfo, final String response) throws Exception {
		if (info.getVersion().startsWith("1.") || info.getVersion().startsWith("2.0."))
			return outputClass.getCollection(collectionInfo, response);
		return Other.getElementCollection(info, collectionInfo, response);
	}

}
