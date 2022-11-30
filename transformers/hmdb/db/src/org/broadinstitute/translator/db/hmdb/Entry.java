package org.broadinstitute.translator.db.hmdb;

public class Entry {

	ID id;

	ID[] equivalent_identifiers;


	public Entry() {
	}


	public void setId(ID id) {
		this.id = id;
	}


	public void setEquivalent_identifiers(ID[] equivalent_identifiers) {
		this.equivalent_identifiers = equivalent_identifiers;
	}


	public static class ID {

		String identifier;

		String label;


		public void setIdentifier(String identifier) {
			this.identifier = identifier;
		}


		public void setLabel(String label) {
			this.label = label;
		}

	}
}
