package transformer;

import java.net.URL;

import apimodels.CollectionInfo;
import apimodels.TransformerInfo;
import transformer.collection.CollectionsEntry;
import transformer.Transformer.Query;

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
		final CollectionsEntry collection = outputClass.getCollection(collectionInfo, response);
		return collection;
	}



}
