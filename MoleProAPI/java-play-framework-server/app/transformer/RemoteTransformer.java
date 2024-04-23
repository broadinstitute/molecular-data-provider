package transformer;

import java.net.URL;

import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.TransformerInfo;
import transformer.collection.CollectionsEntry;
import transformer.elements.CollectionElement;
import transformer.util.HTTP;
import transformer.util.JSON;

public class RemoteTransformer extends Transformer {

	static Transformer createFrom(final TransformerInfo info) {
		return new RemoteTransformer(info);
	}


	protected RemoteTransformer(final TransformerInfo info) {
		super(info);
	}


	@Override
	public CollectionsEntry transform(final TransformerQuery query, final CollectionInfo collectionInfo) throws Exception {
		final URL url = new URL(info.getUrl() + "/transform");
		log.debug(info.getName() + " @ " + url);
		final String json = JSON.mapper.writeValueAsString(query);
		final String response = HTTP.post(url, json);
		final CollectionsEntry collection = getCollection(collectionInfo, response);
		return collection;
	}


	private CollectionsEntry getCollection(final CollectionInfo collectionInfo, final String response) throws Exception {
		Element[] elements = getElementCollection(info.getKnowledgeMap().getOutputClass(), collectionInfo, response);
		for (Element element : elements) {
			CollectionElement.mapElement(info, element);
		}
		return new CollectionsEntry(collectionInfo, elements);
	}

	private static Element[] getElementCollection(final String elementClass, final CollectionInfo collectionInfo, final String response) throws Exception {
		final Element[] elements = JSON.mapper.readValue(response, Element[].class);
		collectionInfo.setElementClass(elementClass);
		collectionInfo.setUrl(Config.config.url().getBaseURL() + "/collection/");
		for (Element element : elements) {
			if (!MoleProDB.addInfo(element)) {
				log.warn("Failed to obtain MoleProDB info for " + element.getId());
			}
		}
		return elements;
	}


}
