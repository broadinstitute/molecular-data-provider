package apimodels;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Names;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Element
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Element   {
  @JsonProperty("id")
  private String id;

  @JsonProperty("biolink_class")
  private String biolinkClass;

  @JsonProperty("identifiers")
  private Map<String, Object> identifiers = new HashMap<>();

  @JsonProperty("alternative_identifiers")
  private List<Map<String, Object>> alternativeIdentifiers = null;

  @JsonProperty("names_synonyms")
  private List<Names> namesSynonyms = null;

  @JsonProperty("attributes")
  private List<Attribute> attributes = null;

  @JsonProperty("connections")
  private List<Connection> connections = null;

  @JsonProperty("source")
  private String source;

  @JsonProperty("provided_by")
  private String providedBy;

  public Element id(String id) {
    this.id = id;
    return this;
  }

   /**
   * Primary identifier of the element.
   * @return id
  **/
  @NotNull
  public String getId() {
    return id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public Element biolinkClass(String biolinkClass) {
    this.biolinkClass = biolinkClass;
    return this;
  }

   /**
   * BioLink class of the element.
   * @return biolinkClass
  **/
  @NotNull
  public String getBiolinkClass() {
    return biolinkClass;
  }

  public void setBiolinkClass(String biolinkClass) {
    this.biolinkClass = biolinkClass;
  }

  public Element identifiers(Map<String, Object> identifiers) {
    this.identifiers = identifiers;
    return this;
  }

  public Element putIdentifiersItem(String key, Object identifiersItem) {
    this.identifiers.put(key, identifiersItem);
    return this;
  }

   /**
   * identifiers of the element.
   * @return identifiers
  **/
  @NotNull
  public Map<String, Object> getIdentifiers() {
    return identifiers;
  }

  public void setIdentifiers(Map<String, Object> identifiers) {
    this.identifiers = identifiers;
  }

  public Element alternativeIdentifiers(List<Map<String, Object>> alternativeIdentifiers) {
    this.alternativeIdentifiers = alternativeIdentifiers;
    return this;
  }

  public Element addAlternativeIdentifiersItem(Map<String, Object> alternativeIdentifiersItem) {
    if (alternativeIdentifiers == null) {
      alternativeIdentifiers = new ArrayList<>();
    }
    alternativeIdentifiers.add(alternativeIdentifiersItem);
    return this;
  }

   /**
   * identifiers of additional chemical structures associated with chemical substance.
   * @return alternativeIdentifiers
  **/
  @Valid
  public List<Map<String, Object>> getAlternativeIdentifiers() {
    return alternativeIdentifiers;
  }

  public void setAlternativeIdentifiers(List<Map<String, Object>> alternativeIdentifiers) {
    this.alternativeIdentifiers = alternativeIdentifiers;
  }

  public Element namesSynonyms(List<Names> namesSynonyms) {
    this.namesSynonyms = namesSynonyms;
    return this;
  }

  public Element addNamesSynonymsItem(Names namesSynonymsItem) {
    if (namesSynonyms == null) {
      namesSynonyms = new ArrayList<>();
    }
    namesSynonyms.add(namesSynonymsItem);
    return this;
  }

   /**
   * Names and synonyms of the element.
   * @return namesSynonyms
  **/
  @Valid
  public List<Names> getNamesSynonyms() {
    return namesSynonyms;
  }

  public void setNamesSynonyms(List<Names> namesSynonyms) {
    this.namesSynonyms = namesSynonyms;
  }

  public Element attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public Element addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Additional information about the element and provenance about collection membership.
   * @return attributes
  **/
  @Valid
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  public Element connections(List<Connection> connections) {
    this.connections = connections;
    return this;
  }

  public Element addConnectionsItem(Connection connectionsItem) {
    if (connections == null) {
      connections = new ArrayList<>();
    }
    connections.add(connectionsItem);
    return this;
  }

   /**
   * connections to elements of the input collection.
   * @return connections
  **/
  @Valid
  public List<Connection> getConnections() {
    return connections;
  }

  public void setConnections(List<Connection> connections) {
    this.connections = connections;
  }

  public Element source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Source of the element
   * @return source
  **/
  @NotNull
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public Element providedBy(String providedBy) {
    this.providedBy = providedBy;
    return this;
  }

   /**
   * Name of a transformer that added the element to the collection.
   * @return providedBy
  **/
  @NotNull
  public String getProvidedBy() {
    return providedBy;
  }

  public void setProvidedBy(String providedBy) {
    this.providedBy = providedBy;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Element element = (Element) o;
    return Objects.equals(id, element.id) &&
        Objects.equals(biolinkClass, element.biolinkClass) &&
        Objects.equals(identifiers, element.identifiers) &&
        Objects.equals(alternativeIdentifiers, element.alternativeIdentifiers) &&
        Objects.equals(namesSynonyms, element.namesSynonyms) &&
        Objects.equals(attributes, element.attributes) &&
        Objects.equals(connections, element.connections) &&
        Objects.equals(source, element.source) &&
        Objects.equals(providedBy, element.providedBy);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, biolinkClass, identifiers, alternativeIdentifiers, namesSynonyms, attributes, connections, source, providedBy);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Element {\n");
    
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    biolinkClass: ").append(toIndentedString(biolinkClass)).append("\n");
    sb.append("    identifiers: ").append(toIndentedString(identifiers)).append("\n");
    sb.append("    alternativeIdentifiers: ").append(toIndentedString(alternativeIdentifiers)).append("\n");
    sb.append("    namesSynonyms: ").append(toIndentedString(namesSynonyms)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
    sb.append("    connections: ").append(toIndentedString(connections)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    providedBy: ").append(toIndentedString(providedBy)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(java.lang.Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }
}

