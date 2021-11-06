package transformer;

import apimodels.CollectionInfo;
import apimodels.TransformerInfo;
import apimodels.TransformerInfo.FunctionEnum;
import transformer.classes.Gene;
import transformer.collection.CollectionsEntry;
import transformer.exception.BadRequestException;
import transformer.exception.InternalServerError;
import transformer.Transformer.Query;

public class InternalTransformer extends Transformer {

	FunctionEnum AGGREGATOR = TransformerInfo.FunctionEnum.AGGREGATOR;


	static Transformer createFrom(final InternalTransformerInfo info) {
		if (info.getName().startsWith("HGNC#")) {
			info.setName(info.getName().substring(5));
			return new Gene.GeneListProducer(info);
		}
		if (info.getName().startsWith("ElementFilter#")) {
			info.setName(info.getName().substring(14));
			return new FilterTransformer.ElementFilterTransformer(info);
		}
		if (info.getName().startsWith("ConnectionFilter#")) {
			info.setName(info.getName().substring(17));
			return new FilterTransformer.ConnectionFilterTransformer(info);
		}
		if (info.chain != null && info.chain.length > 0) {
			return new ChainTransformer(info);
		}
		return new InternalTransformer(info);
	}


	protected InternalTransformer(final TransformerInfo info) {
		super(info);
	}


	@Override
	public CollectionsEntry transform(final Query query, final CollectionInfo collectionInfo) throws Exception {
		if (AGGREGATOR.equals(info.getFunction())) {
			throw new BadRequestException("use /aggregate endpoint to call aggregators");
		}
		throw new InternalServerError("Internal transformer '" + info.getName() + "' not implemented");
	}


	static class InternalTransformerInfo extends TransformerInfo {

		private String[] chain = new String[0];


		public String[] chain() {
			return chain;
		}


		public void setChain(String[] chain) {
			this.chain = chain;
		}
	}
}
