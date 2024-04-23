package transformer;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.CollectionInfo;
import apimodels.Parameter;
import apimodels.Property;
import transformer.collection.CollectionsEntry;
import transformer.exception.BadRequestException;
import transformer.exception.InternalServerError;
import transformer.InternalTransformer.InternalTransformerInfo;

public class ChainTransformer extends InternalTransformer {

	final static Logger log = LoggerFactory.getLogger(ChainTransformer.class);

	private final String[] chain;


	protected ChainTransformer(InternalTransformerInfo info) {
		super(info);
		this.chain = info.chain();
	}


	@Override
	public CollectionsEntry transform(final TransformerQuery srcQuery, final CollectionInfo collectionInfo) throws Exception {
		CollectionsEntry entry = null;
		try {
			for (String transformerName : this.chain) {
				Transformer transformer = Transformers.getTransformer(transformerName);
				List<Property> controls = controls(srcQuery, transformer);
				TransformerQuery query = (entry == null) ? srcQuery.query(controls) : new TransformerQuery(controls, entry);
				entry = transformer.transform(query, new CollectionInfo());
			}
		}
		catch (Exception e) {
			log.warn("Chain transformer failed: ", e);
			throw new InternalServerError("Chain transformer failed: " + e.getMessage(), e);
		}
		return new CollectionsEntry(collectionInfo, entry.getElements());
	}


	private List<Property> controls(final TransformerQuery srcQuery, Transformer transformer) throws BadRequestException {
		final List<Property> controls = new ArrayList<>();
		for (Parameter parameter : transformer.info.getParameters()) {
			String name = parameter.getName();
			List<String> values = srcQuery.getPropertyValue(name);
			if (parameter.getRequired() && values.size() == 0) {
				throw new BadRequestException("required parameter '" + name + "' not specified");
			}
			for (String value : values) {
				controls.add(new Property().name(name).value(value));
			}
		}
		return controls;
	}
}
