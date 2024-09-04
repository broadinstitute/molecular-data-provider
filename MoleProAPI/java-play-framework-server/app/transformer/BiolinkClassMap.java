package transformer;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

public class BiolinkClassMap {

	private String[] alias;

	private List<Prefix> prefixes;

	private String parent;

	private String[] identifierPriority;


	public String[] getAlias() {
		return alias;
	}


	public void setAlias(String[] alias) {
		this.alias = alias;
	}


	public List<Prefix> getPrefixes() {
		return prefixes;
	}


	@JsonProperty("id_prefixes")
	public void setPrefixes(List<Prefix> prefixes) {
		this.prefixes = prefixes;
		List<String> identifierPriority = new ArrayList<String>();
		for (Prefix prefix : prefixes) {
			identifierPriority.add(prefix.field_name);
		}
		this.identifierPriority = identifierPriority.toArray(new String[0]);
	}


	public String getParent() {
		return parent;
	}


	public void setParent(String parent) {
		this.parent = parent;
	}


	public String[] getIdentifierPriority() {
		return identifierPriority;
	}


	public static class Prefix {

		private String biolink_prefix;
		private String field_name;
		private String infores;
		private String molepro_prefix;


		public String getBiolink_prefix() {
			return biolink_prefix;
		}


		public void setBiolink_prefix(String biolink_prefix) {
			this.biolink_prefix = biolink_prefix;
		}


		public String getField_name() {
			return field_name;
		}


		public void setField_name(String field_name) {
			this.field_name = field_name;
		}


		public String getInfores() {
			return infores;
		}


		public void setInfores(String infores) {
			this.infores = infores;
		}


		public String getMolepro_prefix() {
			return molepro_prefix;
		}


		public void setMolepro_prefix(String molepro_prefix) {
			this.molepro_prefix = molepro_prefix;
		}

	}
}
