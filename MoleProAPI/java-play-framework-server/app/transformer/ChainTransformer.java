package transformer;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.ChainQuery;
import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Property;
import transformer.collection.Aggregator;
import transformer.collection.CollectionsEntry;
import transformer.exception.InternalServerError;

public class ChainTransformer {

	final static Logger log = LoggerFactory.getLogger(ChainTransformer.class);

	private final List<ChainQuery> chainQuery;


	protected ChainTransformer(List<ChainQuery> chainQuery) {
		this.chainQuery = chainQuery;
	}


	public Collection transform(String cache) {
		CollectionsEntry union = null;
		CollectionsEntry entry = null;
		try {
			for (ChainQuery chainLink : this.chainQuery) {
				String transformerName = chainLink.getName();
				Transformer transformer = Transformers.getTransformer(transformerName);
				List<Property> controls = chainLink.getControls();
				TransformerQuery query = new TransformerQuery(controls, entry);
				entry = transformer.transform(query, new CollectionInfo());
				if (union == null) {
					union = entry;
				}
				else {
					union = Aggregator.union(Stream.of(union, entry).collect(Collectors.toList()));
				}
			}
			return union.asCollection();
		}
		catch (Exception e) {
			log.warn("Chain transformer failed: ", e);
			throw new InternalServerError("Chain transformer failed: " + e.getMessage(), e);
		}
	}
}
