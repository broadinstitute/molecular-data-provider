package transformer;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

import apimodels.Attribute;
import apimodels.CollectionInfo;
import apimodels.Connection;
import apimodels.MoleProQuery;
import apimodels.Property;
import apimodels.TransformerInfo;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.elements.CollectionElement;
import transformer.exception.BadRequestException;

public abstract class FilterTransformer extends InternalTransformer {

	public FilterTransformer(TransformerInfo info) {
		super(info);
	}


	@Override
	public CollectionInfo transform(final MoleProQuery moleproQuery, final String cache) throws Exception {
		final String collectionId = moleproQuery.getCollectionId();
		final CollectionsEntry inputCollection = Collections.getCollection(collectionId, cache);
		final CollectionsEntry outputCollection = filter(moleproQuery, inputCollection);
		Collections.save(outputCollection);
		return outputCollection.getInfo();
	}


	protected CollectionsEntry filter(final MoleProQuery moleproQuery, final CollectionsEntry inputCollection) throws Exception {
		final ArrayList<CollectionElement> elements = new ArrayList<>();
		for (CollectionElement element : inputCollection.getElements()) {
			final CollectionElement filteredElement = filterElement(new Constraint(moleproQuery), element);
			if (filteredElement != null) {
				elements.add(filteredElement);
			}
		}
		final CollectionInfo collectionInfo = super.createCollection(moleproQuery);
		return new CollectionsEntry(collectionInfo, elements.toArray(new CollectionElement[elements.size()]));
	}


	abstract protected CollectionElement filterElement(final Constraint constraint, final CollectionElement element);


	protected boolean filter(final Constraint constraint, final List<Attribute> attributes) {
		for (Attribute attribute : attributes)
			if (filter(constraint, attribute))
				return true;
		return false;
	}


	private boolean filter(final Constraint constraint, final Attribute attribute) {
		if (constraint.id.equals(attribute.getAttributeTypeId())) {
			if (constraint.compare(attribute.getValue()))
				return true;
		}
		return false;

	}


	static class ElementFilterTransformer extends FilterTransformer {

		public ElementFilterTransformer(final TransformerInfo info) {
			super(info);
		}


		protected CollectionElement filterElement(final Constraint constraint, final CollectionElement element) {
			if (filter(constraint, element.getElement().getAttributes())) {
				return element;
			}
			return null;
		}
	}


	static class ConnectionFilterTransformer extends FilterTransformer {

		public ConnectionFilterTransformer(final TransformerInfo info) {
			super(info);
		}


		protected CollectionElement filterElement(final Constraint constraint, final CollectionElement element) {
			final CollectionElement filteredElement = element.duplicate();
			filteredElement.getElement().setAttributes(element.getElement().getAttributes());
			for (Connection connection : element.getElement().getConnections()) {
				if (filter(constraint, connection.getAttributes())) {
					filteredElement.getElement().getConnections().add(connection);
				}
			}
			if (filteredElement.getElement().getConnections().size() > 0)
				return filteredElement;
			return null;
		}
	}


	static class Constraint {

		final String id;
		final String name;
		final boolean not;
		final Operator operator;
		final ArrayList<String> values;


		Constraint(final MoleProQuery moleproQuery) throws BadRequestException {
			final HashMap<String,ArrayList<String>> params = params(moleproQuery);
			id = getString("id", params);
			name = getString("name", params);
			not = getBoolean("not", params);
			values = params.get("value");
			if (values.size() == 0)
				throw new BadRequestException("Bad constraint, value not specified");
			operator = operator(getString("operator", params));
		}


		private HashMap<String,ArrayList<String>> params(final MoleProQuery moleproQuery) {
			final HashMap<String,ArrayList<String>> params = new HashMap<>();
			params.put("not", new ArrayList<String>());
			params.put("value", new ArrayList<String>());
			for (Property control : moleproQuery.getControls()) {
				if (!params.containsKey(control.getName())) {
					params.put(control.getName(), new ArrayList<String>());
				}
				params.get(control.getName()).add(control.getValue());
			}
			return params;
		}


		private String getString(final String property, final HashMap<String,ArrayList<String>> params) throws BadRequestException {
			if (params.containsKey(property) && params.get(property).size() > 0) {
				return params.get(property).get(0);
			}
			throw new BadRequestException("Bad constraint, " + property + " not specified");
		}


		private boolean getBoolean(final String property, final HashMap<String,ArrayList<String>> params) {
			if (params.containsKey(property) && params.get(property).size() > 0) {
				return params.get(property).get(0).toLowerCase().equals("true");
			}
			return false;
		}


		private Operator operator(final String operator) throws BadRequestException {
			if (operator.equals("<"))
				return new LessOperator();
			if (operator.equals("=="))
				return new EqualsOperator();
			if (operator.equals(">"))
				return new MoreOperator();
			if (operator.equals("match"))
				return new MatchOperator(this.values);
			throw new BadRequestException("Bad constraint, unknown operator: '" + operator + "'");
		}


		public boolean compare(final Object value) {
			boolean comparison = operator.compare(this.values, value.toString());
			return (not) ? !comparison : comparison;
		}
	}


	static abstract class Operator {
		abstract boolean compare(ArrayList<String> constraintValues, String attributeValue);
	}


	static class LessOperator extends Operator {
		boolean compare(final ArrayList<String> constraintValues, final String attributeValue) {
			for (String constraintValue : constraintValues) {
				if (compareValue(constraintValue, attributeValue))
					return true;
			}
			return false;
		}


		private boolean compareValue(final String constraintValue, final String attributeValue) {
			// try integer
			try {
				final long longConstraintValue = Long.parseLong(constraintValue);
				final long longAttributeValue = Long.parseLong(attributeValue);
				return longAttributeValue < longConstraintValue;
			}
			catch (NumberFormatException e) {
			}
			// try float
			try {
				final double doubleConstraintValue = Double.parseDouble(constraintValue);
				final double doubleAttributeValue = Double.parseDouble(attributeValue);
				return doubleAttributeValue < doubleConstraintValue;
			}
			catch (NumberFormatException e) {
			}

			return attributeValue.compareTo(constraintValue) < 0;
		}
	}


	static class EqualsOperator extends Operator {
		boolean compare(final ArrayList<String> constraintValues, final String attributeValue) {
			for (String constraintValue : constraintValues) {
				if (sameValue(constraintValue, attributeValue))
					return true;
			}
			return false;
		}


		private boolean sameValue(final String constraintValue, final String attributeValue) {
			// try integer
			try {
				final long longConstraintValue = Long.parseLong(constraintValue);
				final long longAttributeValue = Long.parseLong(attributeValue);
				return longConstraintValue == longAttributeValue;
			}
			catch (NumberFormatException e) {
			}
			// try float
			try {
				final double doubleConstraintValue = Double.parseDouble(constraintValue);
				final double doubleAttributeValue = Double.parseDouble(attributeValue);
				return doubleAttributeValue == doubleConstraintValue;
			}
			catch (NumberFormatException e) {
			}

			return constraintValue.equals(attributeValue);
		}
	}


	static class MoreOperator extends Operator {
		boolean compare(final ArrayList<String> constraintValues, final String attributeValue) {
			for (String constraintValue : constraintValues) {
				if (sameValue(constraintValue, attributeValue))
					return true;
			}
			return false;
		}


		private boolean sameValue(final String constraintValue, final String attributeValue) {
			// try integer
			try {
				final long longConstraintValue = Long.parseLong(constraintValue);
				final long longAttributeValue = Long.parseLong(attributeValue);
				return longAttributeValue > longConstraintValue;
			}
			catch (NumberFormatException e) {
			}
			// try float
			try {
				final double doubleConstraintValue = Double.parseDouble(constraintValue);
				final double doubleAttributeValue = Double.parseDouble(attributeValue);
				return doubleAttributeValue > doubleConstraintValue;
			}
			catch (NumberFormatException e) {
			}

			return attributeValue.compareTo(constraintValue) > 0;
		}
	}


	static class MatchOperator extends Operator {

		private final ArrayList<Pattern> patterns = new ArrayList<>();


		public MatchOperator(ArrayList<String> constraintValues) throws BadRequestException {
			for (String value : constraintValues) {
				try {
					patterns.add(Pattern.compile(value));
				}
				catch (PatternSyntaxException e) {
					throw new BadRequestException("Pattern syntax exception: '" + value + "'");
				}
			}
		}


		boolean compare(final ArrayList<String> constraintValues, final String attributeValue) {
			for (Pattern pattern : patterns) {
				final Matcher matcher = pattern.matcher(attributeValue);
				if (matcher.matches())
					return true;
			}
			return false;
		}
	}
}
