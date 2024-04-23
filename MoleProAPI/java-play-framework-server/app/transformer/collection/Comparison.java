package transformer.collection;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashMap;
import java.util.List;

import apimodels.AggregationQuery;
import apimodels.ComparisonInfo;
import transformer.exception.BadRequestException;

public abstract class Comparison {

	static final HashMap<String,Comparison> methods = new HashMap<>();

	final String method;


	public Comparison(final String method) {
		this.method = method;
	}


	abstract ComparisonInfo compare(List<CollectionsEntry> collections);


	public static ComparisonInfo compare(final AggregationQuery query, final String cache) throws Exception {
		Comparison method = methods.get(query.getOperation());
		if (method == null)
			throw new BadRequestException("Unknown comparison method '" + query.getOperation() + "'");
		else {
			final List<CollectionsEntry> collections = Aggregator.getCollections(query.getCollectionIds(), cache);
			if (collections.size() == 2) {
				return method.compare(collections);
			}
			else
				throw new BadRequestException("Comparison requires exacly two arguments, " + collections.size() + " were given");
		}
	}


	static class Jaccard extends Comparison {

		public Jaccard() {
			super("Jaccard similarity");
		}


		ComparisonInfo compare(final List<CollectionsEntry> collections) {
			final int intersection = Aggregator.intersection(collections).getElements().length;
			final int setAsize = collections.get(0).getElements().length;
			final int setBsize = collections.get(1).getElements().length;
			final BigDecimal score = new BigDecimal(intersection).divide(new BigDecimal(setAsize + setBsize - intersection), 6, RoundingMode.HALF_UP);
			return new ComparisonInfo().operation(method).score(score);
		}
	}

	static {
		Comparison[] comparisons = new Comparison[] { new Jaccard() };
		for (Comparison comparison : comparisons)
			methods.put(comparison.method, comparison);
	}
}
